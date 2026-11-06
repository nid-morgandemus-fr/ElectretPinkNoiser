================================================================
ELECTRET MICROPHONE CAPSULE TESTING PROTOCOL WITH PINK NOISE
================================================================
Usage : Sorting and comparative verification of electret capsules
================================================================
PART 1 : PROTOCOL STEPS
================================================================
STEP 1 - EQUIPMENT PREPARATION
---------------------------------
- Have a computer with Python installed
- Install the required libraries :
pip install numpy scipy matplotlib
- Prepare a quality speaker (monitoring preferred)
- Prepare an audio recorder (USB sound card or portable recorder)
- Prepare the capsules to be tested, soldered on temporary wires
- Prepare a reference capsule (known to be good)

STEP 2 - PINK NOISE GENERATION
----------------------------------
- Launch the generation script :
python3 generate_pink_noise.py -d 10 -r 44100 -o pink_noise.wav
- Recommended default parameters :
Duration : 10 seconds
Sampling rate : 44100 Hz
Format : WAV 16 bits
- Copy the pink_noise.wav file to a USB drive or leave it on the computer

STEP 3 - TEST DEVICE INSTALLATION
--------------------------------------------
- Place the speaker on a stable surface
- Mark on the floor or table the capsule position at 30 cm from the speaker
- Ensure the room is quiet (no fan, windows closed)
- Connect the recorder to the computer
- Check recording levels (do not saturate)

STEP 4 - REFERENCE RECORDING
----------------------------------------
- Place the reference capsule at the marked position (30 cm)
- Start playing the pink_noise.wav file
- Record for 10 seconds
- Name the file : reference_capsule.wav
- Listen to verify that the sound is present and not saturated

STEP 5 - CAPSULE TESTING
---------------------------
- Remove the reference capsule
- Place the first capsule to be tested EXACTLY at the same position
- Start playing the pink noise
- Record for 10 seconds
- Name the file : capsule_001.wav
- Repeat the operation for each capsule :
capsule_002.wav, capsule_003.wav, etc.
- IMPORTANT : do not move the speaker, do not change the volume

STEP 6 - COMPARATIVE ANALYSIS
-----------------------------
- Place all WAV files in the same folder
- Launch the analysis script :
python3 analyze_capsules.py -i ./recordings/ -o report.pdf
- The script generates a PDF report containing :
- Superimposed frequency spectra
- Summary table of RMS values
- Identification of out-of-tolerance capsules
- Consult the report to identify defective capsules

STEP 7 - RESULTS INTERPRETATION
--------------------------------------
- A capsule is COMPLIANT if its RMS is within tolerance (+/- 6 dB)
- A capsule is REJECTED if its RMS deviates more than 6 dB from the average
- Visually verify the spectra :
- A capsule with a very irregular spectrum is suspicious
- A capsule with excessive background noise should be rejected
- Keep the PDF report for traceability

================================================================
PART 2 : PRACTICAL TIPS
================================================================
REGARDING THE SPEAKER
---------------------
- Use a monitoring speaker with the flattest possible frequency response
- Avoid consumer speakers with boosted bass or accentuated treble
- Place the speaker on a stable support, not directly on a hollow surface
- Do not change the volume between tests (use a mark on the knob)
- If possible, use a quality full-range speaker (e.g., small studio monitor)

REGARDING THE TEST ROOM
---------------------------
- Choose a quiet room, away from outside noise (traffic, air conditioning)
- Avoid highly reverberant rooms (tiles, bare walls)
- If possible, surround the test area with acoustic foam or blankets
- Close windows and turn off fans during tests
- A small furnished room (carpet, curtains, sofa) is often better than a large empty room

REGARDING POSITIONING
----------------------------
- Mark the exact position of each capsule (tape, marker)
- Use a rigid support to hold the capsule (clamp, 3D printed support)
- Respect a fixed distance (30 cm is a good compromise)
- Always orient the capsule on the same axis (facing the speaker)
- Do not touch the capsule during recording (handling noise)

REGARDING RECORDING
---------------------------
- ALWAYS use the same recorder and the same settings
- Check levels before each take (no saturation, no excessive background noise)
- Use a good quality shielded cable between the capsule and the recorder
- Power the capsule with a fresh battery or a stabilized power supply
- Wait 5 seconds before starting the recording (stabilization)
- Record for at least 10 seconds to have a good statistical average

REGARDING THE CAPSULES
-----------------------
- Check the polarity (+/-) before each test (case = negative)
- Ensure the acoustic hole is not blocked by solder or flux
- Handle the capsules with care (sensitive to ESD and heat)
- Do not blow directly on the capsule (risk of membrane damage)
- Test the capsule first with a multimeter (tap test) before recording

REGARDING THE ANALYSIS
--------------------
- The method is RELATIVE, not absolute : it compares capsules to each other
- It does not give the real sensitivity in dBV/Pa
- The measured frequency response also includes the speaker's defects
- A +/- 3 dB deviation between capsules is normal and acceptable
- A deviation greater than 6 dB indicates a problem
- In case of doubt, redo the test with another position or another speaker

REGARDING TRACEABILITY
-------------------------
- Name files explicitly (capsule_001, capsule_002, etc.)
- Keep a text or CSV file listing the tested capsules
- Archive PDF reports with the date and operator's name
- Keep WAV files at least for the duration of production
- Note test conditions (temperature, humidity if relevant)

REGARDING THE METHOD'S LIMITS
------------------------------------
- This method does not replace professional calibration
- It does not allow measuring directivity
- It does not allow measuring harmonic distortion (THD)
- It is sensitive to the room's acoustic conditions
- For official certificates, use a calibrated microphone and an anechoic chamber
- For quick sorting in artisanal production, this method is perfectly adapted

================================================================
PART 3 : USEFUL COMMANDS
================================================================
Generate pink noise :
python3 generate_pink_noise.py -d 10 -r 44100 -o pink_noise.wav
python3 generate_pink_noise.py --duration 30 --rate 48000 --output test.wav
python3 generate_pink_noise.py --voss  (more precise but slower algorithm)

Analyze capsules :
python3 analyze_capsules.py -i ./recordings/ -o report.pdf
python3 analyze_capsules.py --input-dir ./tests/ --threshold 3.0
python3 analyze_capsules.py --pattern "capsule_*.wav"

Check audio files :
ls -lh *.wav
file pink_noise.wav
soxi pink_noise.wav  (if sox is installed)

================================================================
PART 4 : ACCEPTANCE CRITERIA
================================================================
COMPLIANT Capsule :
- RMS within tolerance (+/- 6 dB compared to the average)
- Regular frequency spectrum (no peaks > 3 dB)
- Acceptable background noise (SNR > 40 dB if measurable)
- Correct tap test response with multimeter

Capsule TO VERIFY :
- RMS between 3 and 6 dB deviation from the average
- Spectrum with some irregularities
- Redo the test to confirm

REJECTED Capsule :
- RMS greater than 6 dB deviation from the average
- Very irregular or flat spectrum
- No tap test response
- Excessive background noise (hissing, hum)
- Short-circuit or open-circuit detected with multimeter

================================================================
PART 5 : TROUBLESHOOTING
================================================================
Problem : No sound recorded
- Check the capsule's power supply
- Check soldering and polarity
- Check the cable and connections
- Test the capsule with a multimeter (tap test)

Problem : Saturated sound (clipping)
- Lower the recorder's gain
- Move the capsule away from the speaker
- Lower the speaker's volume

Problem : Excessive background noise
- Change room (quieter)
- Use battery power
- Check cable shielding
- Move away from interference sources (transformers, screens)

Problem : Inconsistent results between two tests
- Verify that the capsule position is identical
- Verify that the speaker volume has not changed
- Wait for the room to be quiet
- Redo the test with the reference capsule to verify

Problem : All capsules seem bad
- Check the speaker (it may not be suitable)
- Check the recorder (incorrect settings)
- Change test room
- Recalibrate with a known-good capsule
