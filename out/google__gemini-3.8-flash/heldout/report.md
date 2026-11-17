# google/gemini-3.8-flash on heldout (25 cards)

Cards scored: 25 (25 with predictions)

F1 on filled fields:      92.4%  (precision 95.8%, recall 89.2%)
Safety-critical fields:   96.2%  (precision 98.5%, recall 94.1%)
Invented values:          2 total, 0.08 per card
Injury boxes F1:          80.5%
Naive field accuracy:     98.4%  (an empty card scores 85.7%)

| Group | F1 | Precision | Recall | Correct | Wrong | Invented | Missed |
|---|---|---|---|---|---|---|---|
| identity | 85.4% | 90.9% | 80.5% | 120 | 12 | 0 | 17 |
| treatments | 88.9% | 96.6% | 82.4% | 28 | 1 | 0 | 5 |
| mechanism | 93.9% | 92.0% | 95.8% | 23 | 0 | 2 | 1 |
| vital_signs | 94.3% | 97.5% | 91.2% | 156 | 4 | 0 | 11 |
| evac | 97.7% | 100.0% | 95.5% | 21 | 0 | 0 | 1 |
| tourniquets | 98.1% | 100.0% | 96.3% | 26 | 0 | 0 | 1 |
| medications | 100.0% | 100.0% | 100.0% | 62 | 0 | 0 | 0 |

## Where the errors come from

- transcription: 27
- extraction: 26
- invented: 2

## Kinds of problem

- left blank: 36
- wrong value: 7
- name/unit spelling: 6
- digit off: 4
- made up: 2

## Errors by group and stage

- identity / transcription: 17
- identity / extraction: 12
- vital_signs / transcription: 8
- vital_signs / extraction: 7
- treatments / extraction: 5
- mechanism / invented: 2
- tourniquets / transcription: 1
- evac / extraction: 1
- mechanism / extraction: 1
- treatments / transcription: 1

## Every error

| file | field | stage | kind | predicted | truth |
|---|---|---|---|---|---|
| ato | tq_right_leg_time | transcription | left blank |  | 1012 |
| ato | breathing_chest_seal | extraction | left blank | False | True |
| cjp | battle_roster | transcription | wrong value | VA62119 | VA6119 |
| dgf | signs_2_avpu | extraction | left blank |  | A - Alert |
| fox | battle_roster | transcription | wrong value | RE88206 | RE8826 |
| inj | time | transcription | digit off | 2050 | 2015 |
| inj | first_responder_name | extraction | name/unit spelling | Quinn, Joe | Quinn, Jo |
| jso | last4 | transcription | left blank |  | 4062 |
| jso | splint | extraction | left blank | False | True |
| jso | first_responder_name | extraction | name/unit spelling | Dunn | Dunn, Ross |
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
| kdb | signs_1_resp_rate | extraction | left blank |  | 22 |
| kdb | signs_1_avpu | transcription | left blank |  | A - Alert |
| kdb | signs_1_pain | extraction | left blank |  | 6 Intense |
| kdb | dressing_hemostatic | extraction | left blank | False | True |
| kdb | dressing_pressure | extraction | left blank | False | True |
| lrh | date | transcription | left blank |  | 01-NOV-26 |
| nwd | time | transcription | left blank |  | 1500 |
| oeu | time | transcription | left blank |  | 1910 |
| oeu | unit | extraction | left blank |  | Signals det |
| oeu | mechanism_burn | invented | made up | True | False |
| oeu | signs_1_avpu | transcription | wrong value | A - Alert | V - Verbal |
| oeu | dressing_type | transcription | wrong value | clingfilm | cling film |
| onh | unit | extraction | name/unit spelling | Royal Army detachment | REME detachment |
| onh | signs_1_avpu | extraction | left blank |  | A - Alert |
| pma | time | transcription | digit off | 1305 | 1306 |
| riq | last4 | transcription | left blank |  | 5290 |
| riq | gender_m | extraction | left blank | False | True |
| riq | time | transcription | left blank |  | 2100 |
| riq | signs_1_spo2 | transcription | digit off | 94 | 95 |
| riq | signs_1_avpu | extraction | left blank |  | A - Alert |
| riq | first_responder_name | extraction | name/unit spelling | Weed, Cal | Reid, Cal |
| rtw | signs_1_time | transcription | left blank |  | 1500 |
| vbf | gender_m | extraction | left blank | False | True |
| xbf | last4 | transcription | left blank |  | 3620 |
| xbf | date | transcription | wrong value | 31-OCT-26 | 30-OCT-26 |
| xqu | signs_1_pulse | extraction | wrong value | 104 | 104 radial |
| xqu | combat_pill_pack | extraction | left blank | False | True |
| xqu | first_responder_name | extraction | name/unit spelling | Guru, Raj | Gurung, Raj |
| xqu | first_responder_last4 | transcription | left blank |  | 9501 |
| xts | signs_1_resp_rate | extraction | digit off | 18 | 16 |
| ynt | battle_roster | extraction | wrong value | SP22214 | SP2214 |
| ynt | mechanism_burn | invented | made up | True | False |
| ynt | first_responder_name | extraction | name/unit spelling | Day | Day, Finn |
