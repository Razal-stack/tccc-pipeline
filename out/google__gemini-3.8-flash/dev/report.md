# google/gemini-3.8-flash on dev (25 cards)

Cards scored: 25 (25 with predictions)

F1 on filled fields:      93.3%  (precision 94.8%, recall 91.8%)
Safety-critical fields:   94.7%  (precision 95.7%, recall 93.8%)
Invented values:          5 total, 0.20 per card
Injury boxes F1:          83.4%
Naive field accuracy:     98.5%  (an empty card scores 83.3%)

| Group | F1 | Precision | Recall | Correct | Wrong | Invented | Missed |
|---|---|---|---|---|---|---|---|
| tourniquets | 82.0% | 86.2% | 78.1% | 25 | 4 | 0 | 3 |
| identity | 89.7% | 91.4% | 88.0% | 139 | 13 | 0 | 6 |
| mechanism | 92.3% | 96.0% | 88.9% | 24 | 0 | 1 | 3 |
| treatments | 92.5% | 96.9% | 88.6% | 31 | 1 | 0 | 3 |
| medications | 94.1% | 94.6% | 93.5% | 87 | 1 | 4 | 5 |
| vital_signs | 97.0% | 97.5% | 96.6% | 197 | 5 | 0 | 2 |
| evac | 97.9% | 100.0% | 95.8% | 23 | 0 | 0 | 1 |

## Where the errors come from

- extraction: 25
- transcription: 22
- invented: 5

## Errors by group and stage

- identity / transcription: 10
- identity / extraction: 9
- vital_signs / transcription: 5
- tourniquets / extraction: 4
- medications / invented: 4
- mechanism / extraction: 3
- tourniquets / transcription: 3
- medications / extraction: 3
- treatments / extraction: 3
- medications / transcription: 3
- vital_signs / extraction: 2
- treatments / transcription: 1
- mechanism / invented: 1
- evac / extraction: 1

## Every error

| file | field | stage | predicted | truth |
|---|---|---|---|---|
| aim | name | transcription | Carr, Jazz | Kaur, Jas |
| aim | mechanism_gsw | extraction | False | True |
| bwt | last4 | transcription |  | 5033 |
| bwt | tq_right_leg_time | extraction |  | 1235 |
| bwt | signs_1_pulse | transcription | 130 carotid | 140 carotid |
| ihg | unit | extraction | 1 Unit | 1 Yorks |
| ihg | tq_right_leg_type | extraction |  | CAT |
| ihg | tq_right_leg_time | transcription | 1425 | 1424 |
| ihg | tq_left_leg_type | extraction |  | CAT |
| ihg | tq_left_leg_time | transcription | 1420 | 1422 |
| ihg | signs_1_pain | extraction |  | 9 Excruciating |
| ihg | other_med_1_route | extraction |  | IV |
| ihg | hypothermia_prevention_type | transcription |  | hypothermia prevention kit |
| ihg | first_responder_name | extraction | Jones | Jones, Sam |
| ihg | first_responder_last4 | transcription | 3319 | 3318 |
| isa | other_med_1_route | extraction |  | IV |
| jql | dressing_type | extraction | burns dressing | burns dressings |
| jql | hypothermia_prevention_type | extraction |  | blizzard blanket |
| jql | first_responder_last4 | transcription |  | 2285 |
| jvq | unit | extraction | 2 Larc | 2 Lancs |
| liq | time | transcription | 1110 | 1100 |
| liq | tq_right_leg_time | extraction | 1102 | 1106 |
| liq | first_responder_name | extraction | Owen, Rhys | Reece, Owen |
| mbs | time | transcription |  | 0340 |
| mbs | signs_1_pain | extraction | 0 None | 9 Excruciating |
| mbs | signs_2_time | transcription | 0450 | 0415 |
| mbs | blood_1_route | extraction |  | IV |
| odw | unit | extraction | 45 Commander | 45 Commando |
| oog | name | extraction | Davis, Rhys | Davies, Rhys |
| oog | date | transcription |  | 04-NOV-26 |
| oog | allergies | transcription | No known allergies | NKA |
| oog | signs_2_time | transcription | 1015 | 0920 |
| pbj | other_med_1_dose | transcription |  | 1 g |
| pbj | other_med_2_dose | transcription |  | 1 g |
| qof | mechanism_artillery | invented | True | False |
| qof | hypothermia_prevention_type | extraction |  | HPMK |
| qof | first_responder_name | extraction | Hogan | Hogan, Ciara |
| roo | other_med_1_name | invented | TXA |  |
| roo | other_med_1_dose | invented | 2 g |  |
| roo | other_med_1_route | invented | IV |  |
| roo | other_med_1_time | invented | 1058 |  |
| uij | mechanism_mvc | extraction | False | True |
| vdi | evac_urgent | extraction | False | True |
| vdi | time | transcription |  | 0715 |
| vdi | mechanism_ied | extraction | False | True |
| vdi | tq_left_leg_time | transcription | 1115 | 0718 |
| vdi | signs_1_pulse | transcription |  | 130 |
| xqh | name | extraction | Murphy, Aoi | Murphy, Aoife |
| xqh | signs_1_bp_diastolic | transcription | 74 | 76 |
| xqh | first_responder_name | extraction | Zayn, Ahmed | Ahmed, Zain |
| xvw | last4 | transcription |  | 7007 |
| zas | other_med_1_time | transcription | 0750 | 0755 |
