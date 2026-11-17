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

| file | field | stage | predicted | truth |
|---|---|---|---|---|
| ato | tq_right_leg_time | transcription |  | 1012 |
| ato | breathing_chest_seal | extraction | False | True |
| cjp | battle_roster | transcription | VA62119 | VA6119 |
| dgf | signs_2_avpu | extraction |  | A - Alert |
| fox | battle_roster | transcription | RE88206 | RE8826 |
| inj | time | transcription | 2050 | 2015 |
| inj | first_responder_name | extraction | Quinn, Joe | Quinn, Jo |
| jso | last4 | transcription |  | 4062 |
| jso | splint | extraction | False | True |
| jso | first_responder_name | extraction | Dunn | Dunn, Ross |
| kdb | evac_priority | extraction | False | True |
| kdb | name | transcription |  | Reid, Fiona |
| kdb | last4 | transcription |  | 6363 |
| kdb | gender_f | extraction | False | True |
| kdb | time | extraction |  | 0405 |
| kdb | service | transcription |  | Army |
| kdb | unit | transcription |  | 29 Commando Royal Artillery |
| kdb | mechanism_artillery | extraction | False | True |
| kdb | signs_1_time | transcription |  | 0420 |
| kdb | signs_1_pulse | transcription |  | 108 radial |
| kdb | signs_1_bp_systolic | transcription |  | 112 |
| kdb | signs_1_bp_diastolic | transcription |  | 70 |
| kdb | signs_1_resp_rate | extraction |  | 22 |
| kdb | signs_1_avpu | transcription |  | A - Alert |
| kdb | signs_1_pain | extraction |  | 6 Intense |
| kdb | dressing_hemostatic | extraction | False | True |
| kdb | dressing_pressure | extraction | False | True |
| lrh | date | transcription |  | 01-NOV-26 |
| nwd | time | transcription |  | 1500 |
| oeu | time | transcription |  | 1910 |
| oeu | unit | extraction |  | Signals det |
| oeu | mechanism_burn | invented | True | False |
| oeu | signs_1_avpu | transcription | A - Alert | V - Verbal |
| oeu | dressing_type | transcription | clingfilm | cling film |
| onh | unit | extraction | Royal Army detachment | REME detachment |
| onh | signs_1_avpu | extraction |  | A - Alert |
| pma | time | transcription | 1305 | 1306 |
| riq | last4 | transcription |  | 5290 |
| riq | gender_m | extraction | False | True |
| riq | time | transcription |  | 2100 |
| riq | signs_1_spo2 | transcription | 94 | 95 |
| riq | signs_1_avpu | extraction |  | A - Alert |
| riq | first_responder_name | extraction | Weed, Cal | Reid, Cal |
| rtw | signs_1_time | transcription |  | 1500 |
| vbf | gender_m | extraction | False | True |
| xbf | last4 | transcription |  | 3620 |
| xbf | date | transcription | 31-OCT-26 | 30-OCT-26 |
| xqu | signs_1_pulse | extraction | 104 | 104 radial |
| xqu | combat_pill_pack | extraction | False | True |
| xqu | first_responder_name | extraction | Guru, Raj | Gurung, Raj |
| xqu | first_responder_last4 | transcription |  | 9501 |
| xts | signs_1_resp_rate | extraction | 18 | 16 |
| ynt | battle_roster | extraction | SP22214 | SP2214 |
| ynt | mechanism_burn | invented | True | False |
| ynt | first_responder_name | extraction | Day | Day, Finn |
