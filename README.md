# Project Tee

**Subtitles for humans! Transcribe and translate your speech in real time, displayed straight on a screen embedded in your shirt.**

## Inspiration

All three teammates had independently converged on an idea of glasses with subtitles for the world around you. After we realized the impracticality of the idea (how could you read subtitles an inch from your eye without technology that we didn't have access to?) we flipped it around: instead of subtitles (with built-in translation!) that only you could see for _everybody else_, what if you could have subtitles for _you_ that everyone else could see? This way, others could understand what you were saying, breaking barriers of language, distance, and physical impairments.  The subtitles needed to be big so that people could easily read them, and somewhere prominent so people you were conversing with could easily find them. We decided on having a large screen in the front of a shirt/hoodie, which comes with the benefits of wearable tech such as easy portability.

## What it does
The device has three main functions. The first is speech transcription in multiple languages, where what you say is turned into text and you can choose the language you're speaking in. The second is speech translation, which currently translates your transcribed speech into English. The final function is displaying subtitles, and your translated speech is displayed on the screen in the front of the wearable.

## How we built it
We took in audio input from a microphone connected to a Raspberry Pi 5, which sends packets of audio every 100 ms to the Google Cloud speech-to-text API, allowing for live near real-time subtitling. We then sent the transcribed text to the Google Cloud translate API to translate the text into English. We sent this translated text to a file, which was read from to create our display using pygame. Finally, we sewed all the components into a hoodie that we modified to become our wearable subtitle device!

## Challenges we ran into
There were no microphones, so we had to take a trip (on e-scooters!) to a nearby computer shop to buy microphones. We took one apart to be less bulky, desoldering and resoldering components in order to free the base components from the plastic encasing.

We had issues with 3D printing parts for different components: at one point our print and the entire 3D printer went missing with no one knowing where it went, and many of our ideas were too large for the 3D printers.

Since we attached everything to a hoodie, there were some issues with device placement and overheating. Our Raspberry Pi 5 reached 85 degrees C, and some adapters were broken due to device placement.

Finally, a persistent problem we had was using Google Cloud's API to switch between recording different languages. We couldn't find many helpful references online, and the entire process was very complicated.

## Accomplishments that we're proud of
We're proud of successfully transcribing text from audio from the taken-apart microphone. We were so proud, in fact, that we celebrated by going to get boba!

## What we learned
We learned four main lessons. The first and second were that the materials you have access to can significantly increase your possibilities or difficulty (having the 7" OLED display helped a lot) but that even given limited materials, you still have the ability to create (when we weren't able to get a microphone from the Hardware Hub, we went out and bought a microphone that was not suited for our purposes and took it apart to make it work for us). The third and fourth were that seemingly simple tasks can be very difficult and time-consuming to do (as we found in the Google Cloud's APIs for transcription and translation) but also that large, complex tasks can be broken down into simple doable bits (the entire project: we definitely couldn't have made it possible without everyone taking on little bits one at a time).

## What's next for Project Tee
In the future, we hope to make the wearable less bulky and more portable by having a flexible OLED display embedded in the shirt, and adding an alternative power source of solar panels. We also hope to support more languages in the future (we currently support five: English, Spanish, French, Mandarin, and Japanese) both to translate from and to, as well as a possible function to automatically detect what language a user is speaking. As the amount of language options increases, we will likely need an app or website as an option for people to change their language options more easily.
