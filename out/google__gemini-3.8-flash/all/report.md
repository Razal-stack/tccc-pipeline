# google/gemini-3.8-flash on all (50 cards)

Cards scored: 50 (50 with predictions)

F1 on filled fields:      94.7%  (precision 97.5%, recall 92.1%; 95% interval 92.3% to 96.6%)
Safety-critical fields:   96.4%  (precision 97.9%, recall 95.0%)
Invented values:          6 total, 0.12 per card
Injury boxes F1:          89.0%
Naive field accuracy:     98.7%  (an empty card scores 84.5%)

| Group | F1 | Precision | Recall | Correct | Wrong | Invented | Missed |
|---|---|---|---|---|---|---|---|
| identity | 91.4% | 96.7% | 86.6% | 266 | 9 | 0 | 32 |
| treatments | 93.9% | 98.4% | 89.9% | 62 | 1 | 0 | 6 |
| mechanism | 94.0% | 95.9% | 92.2% | 47 | 0 | 2 | 4 |
| tourniquets | 94.9% | 94.9% | 94.9% | 56 | 3 | 0 | 0 |
| vital_signs | 96.0% | 98.3% | 93.9% | 352 | 6 | 0 | 17 |
| medications | 97.1% | 97.4% | 96.8% | 150 | 0 | 4 | 5 |
| evac | 98.9% | 100.0% | 97.8% | 45 | 0 | 0 | 1 |

## Where the errors come from

- extraction: 50
- transcription: 34
- invented: 6

## Kinds of problem

- left blank: 65
- digit off: 10
- made up: 6
- wrong value: 5
- name/unit spelling: 4

## Errors by group and stage

- identity / extraction: 25
- identity / transcription: 16
- vital_signs / transcription: 12
- vital_signs / extraction: 11
- treatments / extraction: 7
- mechanism / extraction: 4
- medications / invented: 4
- tourniquets / transcription: 3
- medications / transcription: 3
- medications / extraction: 2
- mechanism / invented: 2
- evac / extraction: 1

## Every error

| file | field | stage | kind | predicted | truth |
|---|---|---|---|---|---|
| aim | name | extraction | name/unit spelling | Carr, Jas | Kaur, Jas |
| aim | mechanism_gsw | extraction | left blank | False | True |
| ato | breathing_chest_seal | extraction | left blank | False | True |
| bwt | last4 | extraction | left blank |  | 5033 |
| bwt | signs_1_pulse | extraction | left blank |  | 140 carotid |
| cjp | battle_roster | extraction | left blank |  | VA6119 |
| fox | battle_roster | extraction | left blank |  | RE8826 |
| ihg | tq_right_leg_time | transcription | digit off | 1425 | 1424 |
| ihg | tq_left_leg_time | transcription | digit off | 1420 | 1422 |
| ihg | signs_1_time | extraction | left blank |  | 1428 |
| ihg | signs_1_pulse | transcription | left blank |  | 128 radial |
| ihg | signs_1_bp_systolic | extraction | left blank |  | 92 |
| ihg | signs_1_bp_diastolic | extraction | left blank |  | 58 |
| ihg | analgesic_1_time | extraction | left blank |  | 1430 |
| ihg | first_responder_name | extraction | name/unit spelling | Jones | Jones, Sam |
| ihg | first_responder_last4 | transcription | digit off | 3319 | 3318 |
| inj | name | extraction | left blank |  | Khan, Imran |
| inj | time | transcription | left blank |  | 2015 |
| inj | first_responder_name | extraction | name/unit spelling | Quinn, Joe | Quinn, Jo |
| jql | first_responder_last4 | transcription | left blank |  | 2285 |
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
| liq | time | transcription | digit off | 1110 | 1100 |
| liq | first_responder_name | extraction | left blank |  | Reece, Owen |
| mbs | time | extraction | left blank |  | 0340 |
| mbs | signs_2_time | transcription | digit off | 0450 | 0415 |
| mbs | signs_2_pulse | transcription | wrong value | 160 radial | 116 radial |
| mbs | blood_1_route | transcription | left blank |  | IV |
| nwd | time | transcription | left blank |  | 1500 |
| oeu | time | transcription | left blank |  | 1910 |
| oeu | mechanism_burn | invented | made up | True | False |
| oeu | signs_1_avpu | transcription | wrong value | A - Alert | V - Verbal |
| oeu | dressing_type | extraction | wrong value | clingfilm | cling film |
| onh | unit | extraction | left blank |  | REME detachment |
| oog | name | extraction | left blank |  | Davies, Rhys |
| oog | date | transcription | left blank |  | 04-NOV-26 |
| oog | signs_2_time | transcription | left blank |  | 0920 |
| oqx | time | extraction | left blank |  | 1615 |
| pbj | other_med_1_dose | transcription | left blank |  | 1 g |
| pbj | other_med_2_dose | transcription | left blank |  | 1 g |
| pma | time | transcription | digit off | 1305 | 1306 |
| qof | first_responder_name | extraction | name/unit spelling | Hogan | Hogan, Ciara |
| riq | time | transcription | left blank |  | 2100 |
| riq | signs_1_spo2 | transcription | digit off | 94 | 95 |
| riq | first_responder_name | extraction | left blank |  | Reid, Cal |
| roo | other_med_1_name | invented | made up | TXA |  |
| roo | other_med_1_dose | invented | made up | 2 g |  |
| roo | other_med_1_route | invented | made up | IV |  |
| roo | other_med_1_time | invented | made up | 1058 |  |
| rtw | signs_1_time | transcription | left blank |  | 1500 |
| ubn | name | extraction | left blank |  | Ahmed, Sara |
| uij | mechanism_mvc | extraction | left blank | False | True |
| vbf | gender_m | extraction | left blank | False | True |
| vdi | time | transcription | left blank |  | 0715 |
| vdi | mechanism_ied | extraction | left blank | False | True |
| vdi | tq_left_leg_time | transcription | digit off | 1715 | 0718 |
| vdi | signs_1_pulse | transcription | left blank |  | 130 |
| xbf | last4 | extraction | left blank |  | 3620 |
| xbf | date | extraction | wrong value | 31-OCT-26 | 30-OCT-26 |
| xqh | name | extraction | left blank |  | Murphy, Aoife |
| xqh | date | extraction | left blank |  | 31-OCT-26 |
| xqh | signs_1_bp_diastolic | extraction | left blank |  | 76 |
| xqh | first_responder_name | extraction | left blank |  | Ahmed, Zain |
| xqu | signs_1_pulse | extraction | wrong value | 104 | 104 radial |
| xqu | combat_pill_pack | extraction | left blank | False | True |
| xqu | first_responder_name | extraction | left blank |  | Gurung, Raj |
| xqu | first_responder_last4 | transcription | left blank |  | 9501 |
| xrp | last4 | extraction | left blank |  | 1176 |
| xts | signs_1_resp_rate | extraction | digit off | 18 | 16 |
| ynt | mechanism_burn | invented | made up | True | False |
| zas | other_med_1_time | extraction | left blank |  | 0755 |
