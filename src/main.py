import queue
import re
import sys
import time
import os
import signal

from google.cloud import speech_v1p1beta1 as speech
import threading

from audio import get_mic, get_audio
from translate import translate_text

# Audio recording parameters
STREAMING_LIMIT = 240000  # 4 minutes
SAMPLE_RATE = 16000
CHUNK_SIZE = int(SAMPLE_RATE / 10)  # 100ms

RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[0;33m"

DISPLAY_FILE = os.path.dirname(os.path.realpath(__file__)) + "/../tmp/todisplay.txt"
LANGUAGE_CODE_FILE = os.path.dirname(os.path.realpath(__file__)) + "/../tmp/langcode.txt"

model = "default"

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.dirname(os.path.realpath(__file__)) + "/../config/sa.speechtotextGoogleAPIAcc.json"

client = None

languages = [
    'en-US',  # English (US)
    'fr-FR',  # French
    'es-ES',  # Spanish
    'cmn-Hans-CN',  # Chinese
    'ja-JP'   # Japanese
]

DEFAULT_INPUT_LANGUAGE = languages[0]
DEFAULT_OUTPUT_LANGUAGE = "en-US"

current_language = DEFAULT_INPUT_LANGUAGE
assert current_language in languages

def get_next_language_code(current_language):
    current_index = languages.index(current_language)
    next_index = (current_index + 1) % len(languages)
    return languages[next_index]


def get_current_time() -> int:
    """Return Current Time in MS.

    Returns:
        int: Current Time in MS.
    """

    return int(round(time.time() * 1000))


class ResumableMicrophoneStream:
    """Opens a recording stream as a generator yielding the audio chunks."""

    def __init__(
        self: object,
        rate: int,
        chunk_size: int,
    ) -> None:
        """Creates a resumable microphone stream.

        Args:
        self: The class instance.
        rate: The audio file's sampling rate.
        chunk_size: The audio file's chunk size.

        returns: None
        """
        self._rate = rate
        self.chunk_size = chunk_size
        self._num_channels = 1
        self._buff = queue.Queue()
        self.closed = True
        self.start_time = get_current_time()
        self.restart_counter = 0
        self.audio_input = []
        self.last_audio_input = []
        self.result_end_time = 0
        self.is_final_end_time = 0
        self.final_request_end_time = 0
        self.bridging_offset = 0
        self.last_transcript_was_final = False
        self.new_stream = True

    def __enter__(self: object) -> object:
        """Opens the stream.

        Args:
        self: The class instance.

        returns: None
        """
        self.closed = False
        return self

    def __exit__(
        self: object,
        type: object,
        value: object,
        traceback: object,
    ) -> object:
        """Closes the stream and releases resources.

        Args:
        self: The class instance.
        type: The exception type.
        value: The exception value.
        traceback: The exception traceback.

        returns: None
        """
        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self._buff.put(None)

    def _fill_buffer(
        self: object,
        in_data: object,
        *args: object,
        **kwargs: object,
    ) -> object:
        """Continuously collect data from the audio stream, into the buffer.

        Args:
        self: The class instance.
        in_data: The audio data as a bytes object.
        args: Additional arguments.
        kwargs: Additional arguments.

        returns: None
        """
        self._buff.put(in_data)
        return None

    def generator(self: object) -> object:
        """Stream Audio from microphone to API and to local buffer

        Args:
            self: The class instance.

        returns:
            The data from the audio stream.
        """
        while not self.closed:
            data = []

            if self.new_stream and self.last_audio_input:
                chunk_time = STREAMING_LIMIT / len(self.last_audio_input)

                if chunk_time != 0:
                    if self.bridging_offset < 0:
                        self.bridging_offset = 0

                    if self.bridging_offset > self.final_request_end_time:
                        self.bridging_offset = self.final_request_end_time

                    chunks_from_ms = round(
                        (self.final_request_end_time - self.bridging_offset)
                        / chunk_time
                    )

                    self.bridging_offset = round(
                        (len(self.last_audio_input) - chunks_from_ms) * chunk_time
                    )

                    for i in range(chunks_from_ms, len(self.last_audio_input)):
                        data.append(self.last_audio_input[i])

                self.new_stream = False

            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()
            self.audio_input.append(chunk)

            if chunk is None:
                return
            data.append(chunk)
            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self._buff.get(block=False)

                    if chunk is None:
                        return
                    data.append(chunk)
                    self.audio_input.append(chunk)

                except queue.Empty:
                    break

            yield b"".join(data)


def Get_Audio():
    # Your external function to get the streaming audio input
    # Replace this with your actual implementation
    mic = get_mic(CHUNK_SIZE / 1000.0, SAMPLE_RATE)
    while True:
        yield get_audio(mic)


def listen_print_loop(responses: object, stream: object, input_language: str, output_language: str) -> None:
    """Iterates through server responses and prints them.

    The responses passed is a generator that will block until a response
    is provided by the server.

    Each response may contain multiple results, and each result may contain
    multiple alternatives; for details, see https://goo.gl/tjCPAU.  Here we
    print only the transcription for the top alternative of the top result.

    In this case, responses are provided for interim results as well. If the
    response is an interim one, print a line feed at the end of it, to allow
    the next result to overwrite it, until the response is a final one. For the
    final one, print a newline to preserve the finalized transcription.

    Arg:
        responses: The responses returned from the API.
        stream: The audio stream to be processed.
    """
    for response in responses:
        if get_current_time() - stream.start_time > STREAMING_LIMIT:
            stream.start_time = get_current_time()
            break

        if not response.results:
            continue

        result = response.results[0]

        if not result.alternatives:
            continue

        transcript = result.alternatives[0].transcript

        result_seconds = 0
        result_micros = 0

        if result.result_end_time.seconds:
            result_seconds = result.result_end_time.seconds

        if result.result_end_time.microseconds:
            result_micros = result.result_end_time.microseconds

        stream.result_end_time = int((result_seconds * 1000) + (result_micros / 1000))

        corrected_time = (
            stream.result_end_time
            - stream.bridging_offset
            + (STREAMING_LIMIT * stream.restart_counter)
        )
        # Display interim results, but with a carriage return at the end of the
        # line, so subsequent lines will overwrite them.

        with open(DISPLAY_FILE, "w") as f:
            if input_language == output_language:
                text = transcript
            else:
                text = translate_text(output_language, transcript)
            f.write(text)

        if result.is_final:
            sys.stdout.write(GREEN)
            sys.stdout.write("\033[K")
            sys.stdout.write(str(corrected_time) + ": " + transcript + "\n")

            stream.is_final_end_time = stream.result_end_time
            stream.last_transcript_was_final = True

            # Exit recognition if any of the transcribed phrases could be one of our keywords.
            if re.search(r"\b(exit|quit)\b", transcript, re.I):
                sys.stdout.write(YELLOW)
                sys.stdout.write("Exiting...\n")
                stream.closed = True
                break
        else:
            sys.stdout.write(RED)
            sys.stdout.write("\033[K")
            sys.stdout.write(str(corrected_time) + ": " + transcript + "\r")

            stream.last_transcript_was_final = False


def main(input_language: str, output_language: str) -> None:
    """start bidirectional streaming from microphone input to speech API"""
    print(f"Beginning transcription {input_language} -> {output_language}")
    global client
    client = speech.SpeechClient()
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=SAMPLE_RATE,
        language_code=input_language,
        max_alternatives=1,
        model = model
    )
    streaming_config = speech.StreamingRecognitionConfig(
        config=config, interim_results=True
    )

    mic_manager = ResumableMicrophoneStream(SAMPLE_RATE, CHUNK_SIZE)

    audio_generator = Get_Audio()

    with mic_manager as stream:
        while not stream.closed:
            stream.audio_input = []
            requests = (
                speech.StreamingRecognizeRequest(audio_content=content)
                for content in audio_generator
            )

            print("Getting responses")
            responses = client.streaming_recognize(streaming_config, requests)
            print("Gottem")

            # Now, put the transcription responses to use.
            listen_print_loop(responses, stream, input_language, output_language)

            if stream.result_end_time > 0:
                stream.final_request_end_time = stream.is_final_end_time
            stream.result_end_time = 0
            stream.last_audio_input = []
            stream.last_audio_input = stream.audio_input
            stream.audio_input = []
            stream.restart_counter = stream.restart_counter + 1

            if not stream.last_transcript_was_final:
                sys.stdout.write("\n")
            stream.new_stream = True


def handle_signal(a, b) -> None:
    global current_language
    current_language = get_next_language_code(current_language)
    global client
    if client is not None:
        client.__exit__(None, None, None)
        client = None
        time.sleep(1)
    print(f"Switching input to {current_language}")
    main(current_language, DEFAULT_OUTPUT_LANGUAGE)
    exit()

if __name__ == "__main__":
    if len(sys.argv) == 2:
        if sys.argv[1] == '-l':
            print("Available languages:")
            for l in languages:
                print(f"  {l}")
            exit(0)
        else:
            inlang = sys.argv[1]
    else:
        inlang = DEFAULT_INPUT_LANGUAGE
    outlang = DEFAULT_OUTPUT_LANGUAGE

    signal.signal(signal.SIGUSR1, handle_signal)
    main(inlang, outlang)
