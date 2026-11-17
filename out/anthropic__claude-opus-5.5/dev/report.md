# anthropic/claude-opus-5.5 on dev (25 cards)

Cards scored: 25 (25 with predictions)

F1 on filled fields:      93.0%  (precision 95.6%, recall 90.6%)
Safety-critical fields:   94.1%  (precision 95.9%, recall 92.4%)
Invented values:          4 total, 0.16 per card
Injury boxes F1:          87.8%
Naive field accuracy:     98.3%  (an empty card scores 83.3%)

| Group | F1 | Precision | Recall | Correct | Wrong | Invented | Missed |
|---|---|---|---|---|---|---|---|
| tourniquets | 82.0% | 86.2% | 78.1% | 25 | 4 | 0 | 3 |
| identity | 90.8% | 93.9% | 88.0% | 139 | 9 | 0 | 10 |
| treatments | 90.9% | 96.8% | 85.7% | 30 | 1 | 0 | 4 |
| medications | 91.7% | 94.3% | 89.2% | 83 | 1 | 4 | 9 |
| mechanism | 94.1% | 100.0% | 88.9% | 24 | 0 | 0 | 3 |
| evac | 95.7% | 100.0% | 91.7% | 22 | 0 | 0 | 2 |
| vital_signs | 96.8% | 97.5% | 96.1% | 196 | 5 | 0 | 3 |

## Where the errors come from

- extraction: 31
- transcription: 23
- invented: 4

## Errors by group and stage

- identity / extraction: 10
- identity / transcription: 9
- vital_signs / transcription: 5
- medications / extraction: 5
- medications / transcription: 5
- tourniquets / extraction: 4
- treatments / extraction: 4
- medications / invented: 4
- mechanism / extraction: 3
- tourniquets / transcription: 3
- vital_signs / extraction: 3
- evac / extraction: 2
- treatments / transcription: 1

## Every error

| file | field | stage | predicted | truth |
|---|---|---|---|---|
| aim | name | transcription | Carr, Jazz | Kaur, Jas |
| aim | mechanism_gsw | extraction | False | True |
| bwt | last4 | transcription |  | 5033 |
| bwt | tq_right_leg_time | extraction |  | 1235 |
| bwt | signs_1_pulse | transcription | 130 carotid | 140 carotid |
| ihg | evac_urgent | extraction | False | True |
| ihg | unit | extraction |  | 1 Yorks |
| ihg | tq_right_leg_type | extraction |  | CAT |
| ihg | tq_right_leg_time | transcription | 1425 | 1424 |
| ihg | tq_left_leg_type | extraction |  | CAT |
| ihg | tq_left_leg_time | transcription | 1420 | 1422 |
| ihg | signs_1_avpu | extraction |  | V - Verbal |
| ihg | signs_1_pain | extraction |  | 9 Excruciating |
| ihg | other_med_1_route | extraction |  | IV |
| ihg | hypothermia_prevention | extraction | False | True |
| ihg | hypothermia_prevention_type | transcription |  | hypothermia prevention kit |
| ihg | first_responder_name | extraction | Jones | Jones, Sam |
| ihg | first_responder_last4 | transcription | 3319 | 3318 |
| isa | other_med_1_route | extraction |  | IV |
| jql | dressing_type | extraction | burns dressing | burns dressings |
| jql | hypothermia_prevention_type | extraction |  | blizzard blanket |
| jql | first_responder_last4 | transcription |  | 2285 |
| jvq | unit | extraction |  | 2 Lancs |
| liq | time | transcription | 1110 | 1100 |
| liq | tq_right_leg_time | extraction | 1102 | 1106 |
| liq | first_responder_name | extraction | Owen, Rhys | Reece, Owen |
| mbs | time | transcription |  | 0340 |
| mbs | signs_1_pain | extraction | 0 None | 9 Excruciating |
| mbs | signs_2_time | transcription | 0450 | 0415 |
| mbs | blood_1_route | extraction |  | IV |
| oog | name | extraction | Davis, Rhys | Davies, Rhys |
| oog | date | transcription |  | 04-NOV-26 |
| oog | signs_2_time | transcription | 1015 | 0920 |
| pbj | other_med_1_name | transcription |  | TXA |
| pbj | other_med_1_dose | transcription |  | 1 g |
| pbj | other_med_1_time | extraction |  | 0900 |
| pbj | other_med_2_name | transcription |  | TXA |
| pbj | other_med_2_dose | transcription |  | 1 g |
| pbj | other_med_2_time | extraction |  | 0920 |
| qof | hypothermia_prevention_type | extraction |  | HPMK |
| qof | first_responder_name | extraction | Hogan | Hogan, Ciara |
| roo | other_med_1_name | invented | TXA |  |
| roo | other_med_1_dose | invented | 2 g |  |
| roo | other_med_1_route | invented | IV |  |
| roo | other_med_1_time | invented | 1058 |  |
| sfw | last4 | extraction |  | 2771 |
| sfw | unit | extraction |  | 2 Para |
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
