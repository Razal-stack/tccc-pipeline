# google/gemini-4-argon on heldout (25 cards)

Cards scored: 25 (25 with predictions)

F1 on filled fields:      92.4%  (precision 95.4%, recall 89.6%; 95% interval 87.0% to 96.3%)
Safety-critical fields:   95.2%  (precision 96.8%, recall 93.7%)
Invented values:          9 total, 0.36 per card
Injury boxes F1:          80.5%
Naive field accuracy:     98.2%  (an empty card scores 85.7%)

| Group | F1 | Precision | Recall | Correct | Wrong | Invented | Missed |
|---|---|---|---|---|---|---|---|
| identity | 87.8% | 94.6% | 81.9% | 122 | 7 | 0 | 20 |
| treatments | 87.9% | 90.6% | 85.3% | 29 | 1 | 2 | 4 |
| vital_signs | 92.2% | 94.5% | 90.1% | 154 | 4 | 5 | 13 |
| mechanism | 93.9% | 92.0% | 95.8% | 23 | 0 | 2 | 1 |
| evac | 97.7% | 100.0% | 95.5% | 21 | 0 | 0 | 1 |
| tourniquets | 100.0% | 100.0% | 100.0% | 27 | 0 | 0 | 0 |
| medications | 100.0% | 100.0% | 100.0% | 62 | 0 | 0 | 0 |

## Where the errors come from

- transcription: 26
- extraction: 25
- invented: 9

## Kinds of problem

- left blank: 39
- made up: 9
- digit off: 4
- name/unit spelling: 4
- wrong value: 4

## Errors by group and stage

- identity / transcription: 17
- identity / extraction: 10
- vital_signs / extraction: 9
- vital_signs / transcription: 8
- vital_signs / invented: 5
- treatments / extraction: 4
- treatments / invented: 2
- mechanism / invented: 2
- evac / extraction: 1
- mechanism / extraction: 1
- treatments / transcription: 1

## Every error

| file | field | stage | kind | predicted | truth |
|---|---|---|---|---|---|
| ato | breathing_chest_seal | extraction | left blank | False | True |
| cjp | battle_roster | transcription | left blank |  | VA6119 |
| fox | battle_roster | transcription | left blank |  | RE8826 |
| fox | gender_m | extraction | left blank | False | True |
| inj | time | transcription | digit off | 2050 | 2015 |
| inj | first_responder_name | extraction | name/unit spelling | Quinn, Joe | Quinn, Jo |
| jso | last4 | transcription | left blank |  | 4062 |
| jso | splint | extraction | left blank | False | True |
| kdb | evac_priority | extraction | left blank | False | True |
| kdb | name | transcription | left blank |  | Reid, Fiona |
| kdb | last4 | transcription | left blank |  | 6363 |
| kdb | gender_f | extraction | left blank | False | True |
| kdb | time | extraction | left blank |  | 0405 |
| kdb | service | transcription | left blank |  | Army |
| kdb | unit | transcription | left blank |  | 29 Commando Royal Artillery |
| kdb | mechanism_artillery | extraction | left blank | False | True |
| kdb | signs_1_time | transcription | left blank |  | 0420 |
| kdb | signs_1_pulse | transcription | left blank |  | 108 radial |
| kdb | signs_1_bp_systolic | transcription | left blank |  | 112 |
| kdb | signs_1_bp_diastolic | transcription | left blank |  | 70 |
| kdb | signs_1_avpu | transcription | left blank |  | A - Alert |
| kdb | signs_1_pain | extraction | left blank |  | 6 Intense |
| kdb | dressing_hemostatic | extraction | left blank | False | True |
| kdb | dressing_pressure | extraction | left blank | False | True |
| lrh | date | transcription | left blank |  | 01-NOV-26 |
| lrh | dressing_other | invented | made up | True | False |
| nwd | time | transcription | left blank |  | 1500 |
| oeu | last4 | extraction | left blank |  | 5822 |
| oeu | time | transcription | left blank |  | 1910 |
| oeu | unit | extraction | left blank |  | Signals det |
| oeu | mechanism_burn | invented | made up | True | False |
| oeu | signs_1_avpu | transcription | wrong value | A - Alert | V - Verbal |
| oeu | dressing_type | transcription | wrong value | clingfilm | cling film |
| onh | unit | extraction | left blank |  | REME detachment |
| onh | signs_1_avpu | extraction | left blank |  | A - Alert |
| pma | time | transcription | digit off | 1305 | 1306 |
| riq | last4 | transcription | left blank |  | 5290 |
| riq | time | transcription | left blank |  | 2100 |
| riq | signs_1_pulse | extraction | left blank |  | 110 radial |
| riq | signs_1_resp_rate | extraction | left blank |  | 28 |
| riq | signs_1_spo2 | transcription | digit off | 90 | 95 |
| riq | signs_1_avpu | extraction | left blank |  | A - Alert |
| riq | signs_1_pain | extraction | left blank |  | 7 Very Intense |
| riq | signs_2_pulse | invented | made up | 110 radial |  |
| riq | signs_2_resp_rate | invented | made up | 28 |  |
| riq | signs_2_spo2 | invented | made up | 94 |  |
| riq | signs_2_avpu | invented | made up | A - Alert |  |
| riq | signs_2_pain | invented | made up | 7 Very Intense |  |
| riq | airway_intact | invented | made up | True | False |
| riq | first_responder_name | extraction | name/unit spelling | Weed, Cal | Reid, Cal |
| rtw | signs_1_time | transcription | left blank |  | 1500 |
| vbf | signs_1_resp_rate | extraction | left blank |  | 30 |
| xbf | last4 | transcription | left blank |  | 3620 |
| xbf | date | transcription | wrong value | 31-OCT-26 | 30-OCT-26 |
| xqu | signs_1_pulse | extraction | wrong value | 104 | 104 radial |
| xqu | first_responder_name | extraction | name/unit spelling | Guru, Raj | Gurung, Raj |
| xqu | first_responder_last4 | transcription | left blank |  | 9501 |
| xts | signs_1_resp_rate | extraction | digit off | 18 | 16 |
| ynt | mechanism_burn | invented | made up | True | False |
| ynt | first_responder_name | extraction | name/unit spelling | Day | Day, Finn |
