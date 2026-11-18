# google/gemini-3.8-flash on heldout (25 cards)

Cards scored: 25 (25 with predictions)

F1 on filled fields:      93.8%  (precision 97.6%, recall 90.4%; 95% interval 88.9% to 96.9%)
Safety-critical fields:   96.8%  (precision 98.6%, recall 95.1%)
Invented values:          2 total, 0.08 per card
Injury boxes F1:          80.5%
Naive field accuracy:     98.6%  (an empty card scores 85.7%)

| Group | F1 | Precision | Recall | Correct | Wrong | Invented | Missed |
|---|---|---|---|---|---|---|---|
| treatments | 87.1% | 96.4% | 79.4% | 27 | 1 | 0 | 6 |
| identity | 89.5% | 96.9% | 83.2% | 124 | 4 | 0 | 21 |
| mechanism | 93.9% | 92.0% | 95.8% | 23 | 0 | 2 | 1 |
| vital_signs | 94.9% | 97.5% | 92.4% | 158 | 4 | 0 | 9 |
| evac | 97.7% | 100.0% | 95.5% | 21 | 0 | 0 | 1 |
| tourniquets | 100.0% | 100.0% | 100.0% | 27 | 0 | 0 | 0 |
| medications | 100.0% | 100.0% | 100.0% | 62 | 0 | 0 | 0 |

## Where the errors come from

- extraction: 29
- transcription: 18
- invented: 2

## Kinds of problem

- left blank: 38
- digit off: 4
- wrong value: 4
- made up: 2
- name/unit spelling: 1

## Errors by group and stage

- identity / extraction: 14
- identity / transcription: 11
- treatments / extraction: 7
- vital_signs / transcription: 7
- vital_signs / extraction: 6
- mechanism / invented: 2
- evac / extraction: 1
- mechanism / extraction: 1

## Every error

| file | field | stage | kind | predicted | truth |
|---|---|---|---|---|---|
| ato | breathing_chest_seal | extraction | left blank | False | True |
| cjp | battle_roster | extraction | left blank |  | VA6119 |
| fox | battle_roster | extraction | left blank |  | RE8826 |
| inj | name | extraction | left blank |  | Khan, Imran |
| inj | time | transcription | left blank |  | 2015 |
| inj | first_responder_name | extraction | name/unit spelling | Quinn, Joe | Quinn, Jo |
| jso | last4 | transcription | digit off | 4962 | 4062 |
| jso | combat_pill_pack | extraction | left blank | False | True |
| jso | splint | extraction | left blank | False | True |
| jso | first_responder_last4 | extraction | left blank |  | 3855 |
| kdb | evac_priority | extraction | left blank | False | True |
| kdb | name | transcription | left blank |  | Reid, Fiona |
| kdb | last4 | transcription | left blank |  | 6363 |
| kdb | gender_f | extraction | left blank | False | True |
| kdb | service | transcription | left blank |  | Army |
| kdb | unit | transcription | left blank |  | 29 Commando Royal Artillery |
| kdb | mechanism_artillery | extraction | left blank | False | True |
| kdb | signs_1_time | transcription | left blank |  | 0420 |
| kdb | signs_1_pulse | transcription | left blank |  | 108 radial |
| kdb | signs_1_bp_systolic | transcription | left blank |  | 112 |
| kdb | signs_1_bp_diastolic | transcription | left blank |  | 70 |
| kdb | signs_1_resp_rate | extraction | left blank |  | 22 |
| kdb | signs_1_spo2 | extraction | left blank |  | 95 |
| kdb | signs_1_avpu | extraction | left blank |  | A - Alert |
| kdb | signs_1_pain | extraction | left blank |  | 6 Intense |
| kdb | dressing_hemostatic | extraction | left blank | False | True |
| kdb | dressing_pressure | extraction | left blank | False | True |
| nwd | time | transcription | left blank |  | 1500 |
| oeu | time | transcription | left blank |  | 1910 |
| oeu | mechanism_burn | invented | made up | True | False |
| oeu | signs_1_avpu | transcription | wrong value | A - Alert | V - Verbal |
| oeu | dressing_type | extraction | wrong value | clingfilm | cling film |
| onh | unit | extraction | left blank |  | REME detachment |
| oqx | time | extraction | left blank |  | 1615 |
| pma | time | transcription | digit off | 1305 | 1306 |
| riq | time | transcription | left blank |  | 2100 |
| riq | signs_1_spo2 | transcription | digit off | 94 | 95 |
| riq | first_responder_name | extraction | left blank |  | Reid, Cal |
| rtw | signs_1_time | transcription | left blank |  | 1500 |
| ubn | name | extraction | left blank |  | Ahmed, Sara |
| vbf | gender_m | extraction | left blank | False | True |
| xbf | last4 | extraction | left blank |  | 3620 |
| xbf | date | extraction | wrong value | 31-OCT-26 | 30-OCT-26 |
| xqu | signs_1_pulse | extraction | wrong value | 104 | 104 radial |
| xqu | combat_pill_pack | extraction | left blank | False | True |
| xqu | first_responder_name | extraction | left blank |  | Gurung, Raj |
| xqu | first_responder_last4 | transcription | left blank |  | 9501 |
| xts | signs_1_resp_rate | extraction | digit off | 18 | 16 |
| ynt | mechanism_burn | invented | made up | True | False |
