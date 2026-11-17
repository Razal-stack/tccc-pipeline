# google/gemini-3.8-flash on all (50 cards)

Cards scored: 50 (50 with predictions)

F1 on filled fields:      94.0%  (precision 95.9%, recall 92.3%)
Safety-critical fields:   96.2%  (precision 97.1%, recall 95.3%)
Invented values:          7 total, 0.14 per card
Injury boxes F1:          89.0%
Naive field accuracy:     98.7%  (an empty card scores 84.5%)

| Group | F1 | Precision | Recall | Correct | Wrong | Invented | Missed |
|---|---|---|---|---|---|---|---|
| identity | 89.5% | 93.0% | 86.3% | 265 | 20 | 0 | 22 |
| mechanism | 94.0% | 95.9% | 92.2% | 47 | 0 | 2 | 4 |
| treatments | 94.0% | 96.9% | 91.3% | 63 | 1 | 1 | 5 |
| tourniquets | 94.9% | 94.9% | 94.9% | 56 | 3 | 0 | 0 |
| vital_signs | 95.9% | 97.5% | 94.4% | 354 | 9 | 0 | 12 |
| medications | 96.5% | 96.2% | 96.8% | 150 | 2 | 4 | 3 |
| evac | 98.9% | 100.0% | 97.8% | 45 | 0 | 0 | 1 |

## Where the errors come from

- transcription: 46
- extraction: 36
- invented: 7

## Kinds of problem

- left blank: 47
- digit off: 14
- name/unit spelling: 12
- wrong value: 9
- made up: 7

## Errors by group and stage

- identity / transcription: 24
- identity / extraction: 18
- vital_signs / transcription: 14
- vital_signs / extraction: 7
- treatments / extraction: 5
- mechanism / extraction: 4
- medications / transcription: 4
- medications / invented: 4
- tourniquets / transcription: 3
- mechanism / invented: 2
- medications / extraction: 1
- evac / extraction: 1
- treatments / transcription: 1
- treatments / invented: 1

## Every error

| file | field | stage | kind | predicted | truth |
|---|---|---|---|---|---|
| aim | name | extraction | name/unit spelling | Carr, Jas | Kaur, Jas |
| aim | mechanism_gsw | extraction | left blank | False | True |
| ato | breathing_chest_seal | extraction | left blank | False | True |
| bwt | last4 | transcription | left blank |  | 5033 |
| cjp | battle_roster | transcription | wrong value | VA62119 | VA6119 |
| dgf | signs_2_avpu | extraction | left blank |  | A - Alert |
| fox | battle_roster | transcription | wrong value | RE88206 | RE8826 |
| ihg | tq_right_leg_time | transcription | digit off | 1425 | 1424 |
| ihg | tq_left_leg_time | transcription | digit off | 1420 | 1422 |
| ihg | signs_1_pulse | transcription | wrong value | 108 radial | 128 radial |
| ihg | analgesic_1_time | extraction | digit off | 1432 | 1430 |
| ihg | first_responder_name | extraction | name/unit spelling | Jones | Jones, Sam |
| ihg | first_responder_last4 | transcription | digit off | 3319 | 3318 |
| inj | time | transcription | digit off | 2050 | 2015 |
| inj | first_responder_name | extraction | name/unit spelling | Quinn, Joe | Quinn, Jo |
| jql | first_responder_last4 | transcription | left blank |  | 2285 |
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
| liq | time | transcription | digit off | 1110 | 1100 |
| liq | first_responder_name | extraction | name/unit spelling | Rhys, Owen | Reece, Owen |
| lrh | date | transcription | left blank |  | 01-NOV-26 |
| mbs | signs_2_time | transcription | digit off | 0450 | 0415 |
| mbs | signs_2_pulse | transcription | wrong value | 160 radial | 116 radial |
| mbs | blood_1_route | transcription | left blank |  | IV |
| nwd | time | transcription | left blank |  | 1500 |
| oeu | time | transcription | left blank |  | 1910 |
| oeu | unit | extraction | left blank |  | Signals det |
| oeu | mechanism_burn | invented | made up | True | False |
| oeu | signs_1_avpu | transcription | wrong value | A - Alert | V - Verbal |
| oeu | dressing_type | transcription | wrong value | clingfilm | cling film |
| onh | unit | extraction | name/unit spelling | Royal Army detachment | REME detachment |
| onh | signs_1_avpu | extraction | left blank |  | A - Alert |
| oog | date | transcription | left blank |  | 04-NOV-26 |
| oog | signs_2_time | transcription | digit off | 0915 | 0920 |
| pbj | other_med_1_dose | transcription | left blank |  | 1 g |
| pbj | other_med_2_dose | transcription | left blank |  | 1 g |
| pma | time | transcription | digit off | 1305 | 1306 |
| qof | first_responder_name | extraction | name/unit spelling | Hogan | Hogan, Ciara |
| riq | last4 | transcription | left blank |  | 5290 |
| riq | gender_m | extraction | left blank | False | True |
| riq | time | transcription | left blank |  | 2100 |
| riq | signs_1_spo2 | transcription | digit off | 94 | 95 |
| riq | signs_1_avpu | extraction | left blank |  | A - Alert |
| riq | first_responder_name | extraction | name/unit spelling | Weed, Cal | Reid, Cal |
| roo | dressing_pressure | invented | made up | True | False |
| roo | other_med_1_name | invented | made up | TXA |  |
| roo | other_med_1_dose | invented | made up | 2 g |  |
| roo | other_med_1_route | invented | made up | IV |  |
| roo | other_med_1_time | invented | made up | 1058 |  |
| rtw | signs_1_time | transcription | left blank |  | 1500 |
| uij | mechanism_mvc | extraction | left blank | False | True |
| vbf | gender_m | extraction | left blank | False | True |
| vdi | time | transcription | left blank |  | 0715 |
| vdi | mechanism_ied | extraction | left blank | False | True |
| vdi | tq_left_leg_time | transcription | digit off | 1715 | 0718 |
| vdi | signs_1_pulse | transcription | left blank |  | 130 |
| xbf | last4 | transcription | left blank |  | 3620 |
| xbf | date | transcription | wrong value | 31-OCT-26 | 30-OCT-26 |
| xqh | name | extraction | name/unit spelling | Murphy, Aoi | Murphy, Aoife |
| xqh | signs_1_bp_diastolic | transcription | digit off | 74 | 76 |
| xqh | first_responder_name | extraction | name/unit spelling | Ahmed, Zayn | Ahmed, Zain |
| xqu | signs_1_pulse | extraction | wrong value | 104 | 104 radial |
| xqu | combat_pill_pack | extraction | left blank | False | True |
| xqu | first_responder_name | extraction | name/unit spelling | Guru, Raj | Gurung, Raj |
| xqu | first_responder_last4 | transcription | left blank |  | 9501 |
| xts | signs_1_resp_rate | extraction | digit off | 18 | 16 |
| xvw | last4 | transcription | left blank |  | 7007 |
| ynt | battle_roster | extraction | wrong value | SP22214 | SP2214 |
| ynt | mechanism_burn | invented | made up | True | False |
| ynt | first_responder_name | extraction | name/unit spelling | Day | Day, Finn |
| zas | other_med_1_time | transcription | digit off | 0750 | 0755 |
