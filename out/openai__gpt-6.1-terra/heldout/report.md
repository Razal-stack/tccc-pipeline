# openai/gpt-6.1-terra on heldout (25 cards)

Cards scored: 25 (25 with predictions)

F1 on filled fields:      91.8%  (precision 96.0%, recall 87.9%; 95% interval 86.2% to 95.7%)
Safety-critical fields:   94.3%  (precision 96.7%, recall 92.0%)
Invented values:          5 total, 0.20 per card
Injury boxes F1:          78.5%
Naive field accuracy:     98.1%  (an empty card scores 85.7%)

| Group | F1 | Precision | Recall | Correct | Wrong | Invented | Missed |
|---|---|---|---|---|---|---|---|
| identity | 86.2% | 93.7% | 79.9% | 119 | 8 | 0 | 22 |
| vital_signs | 91.8% | 95.0% | 88.9% | 152 | 4 | 4 | 15 |
| treatments | 92.1% | 100.0% | 85.3% | 29 | 0 | 0 | 5 |
| mechanism | 95.8% | 95.8% | 95.8% | 23 | 0 | 1 | 1 |
| tourniquets | 96.3% | 96.3% | 96.3% | 26 | 1 | 0 | 0 |
| evac | 97.7% | 100.0% | 95.5% | 21 | 0 | 0 | 1 |
| medications | 98.4% | 100.0% | 96.8% | 60 | 0 | 0 | 2 |

## Where the errors come from

- extraction: 34
- transcription: 25
- invented: 5

## Kinds of problem

- left blank: 46
- digit off: 5
- name/unit spelling: 5
- made up: 5
- wrong value: 3

## Errors by group and stage

- identity / transcription: 17
- identity / extraction: 13
- vital_signs / extraction: 11
- vital_signs / transcription: 8
- treatments / extraction: 5
- vital_signs / invented: 4
- medications / extraction: 2
- evac / extraction: 1
- mechanism / extraction: 1
- mechanism / invented: 1
- tourniquets / extraction: 1

## Every error

| file | field | stage | kind | predicted | truth |
|---|---|---|---|---|---|
| ato | breathing_chest_seal | extraction | left blank | False | True |
| cjp | battle_roster | transcription | left blank |  | VA6119 |
| cjp | analgesic_1_dose | extraction | left blank |  | 800 mcg |
| dgf | signs_2_avpu | extraction | left blank |  | A - Alert |
| fox | battle_roster | transcription | left blank |  | RE8826 |
| fox | gender_m | extraction | left blank | False | True |
| inj | time | transcription | digit off | 2050 | 2015 |
| inj | analgesic_1_dose | extraction | left blank |  | 800 mcg |
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
| oeu | last4 | extraction | left blank |  | 5822 |
| oeu | time | transcription | left blank |  | 1910 |
| oeu | unit | extraction | left blank |  | Signals det |
| oeu | mechanism_burn | invented | made up | True | False |
| oeu | signs_1_avpu | transcription | wrong value | A - Alert | V - Verbal |
| onh | unit | extraction | left blank |  | REME detachment |
| onh | signs_1_avpu | extraction | left blank |  | A - Alert |
| oqx | tq_right_arm_time | extraction | digit off | 1602 | 1620 |
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
| riq | signs_2_pain | invented | made up | 7 Very Intense |  |
| riq | first_responder_name | extraction | name/unit spelling | Weed, Cal | Reid, Cal |
| rtw | signs_1_time | transcription | left blank |  | 1500 |
| vbf | gender_m | extraction | left blank | False | True |
| vbf | signs_1_resp_rate | extraction | left blank |  | 30 |
| xbf | last4 | transcription | left blank |  | 3620 |
| xbf | date | transcription | wrong value | 31-OCT-26 | 30-OCT-26 |
| xqu | signs_1_pulse | extraction | wrong value | 104 | 104 radial |
| xqu | combat_pill_pack | extraction | left blank | False | True |
| xqu | first_responder_name | extraction | name/unit spelling | Guru, Raj | Gurung, Raj |
| xqu | first_responder_last4 | transcription | left blank |  | 9501 |
| xts | signs_1_resp_rate | extraction | digit off | 18 | 16 |
| ynt | battle_roster | extraction | left blank |  | SP2214 |
| ynt | first_responder_name | extraction | name/unit spelling | Day, Pin | Day, Finn |
