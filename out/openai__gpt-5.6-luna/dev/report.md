# openai/gpt-5.6-luna on dev (25 cards)

Cards scored: 25 (25 with predictions)

F1 on filled fields:      91.7%  (precision 93.3%, recall 90.2%)
Safety-critical fields:   93.0%  (precision 94.5%, recall 91.5%)
Invented values:          14 total, 0.56 per card
Injury boxes F1:          83.6%
Naive field accuracy:     98.0%  (an empty card scores 83.3%)

| Group | F1 | Precision | Recall | Correct | Wrong | Invented | Missed |
|---|---|---|---|---|---|---|---|
| tourniquets | 80.6% | 83.3% | 78.1% | 25 | 3 | 2 | 4 |
| mechanism | 88.9% | 88.9% | 88.9% | 24 | 0 | 3 | 3 |
| medications | 89.4% | 93.0% | 86.0% | 80 | 2 | 4 | 11 |
| identity | 89.6% | 92.0% | 87.3% | 138 | 12 | 0 | 8 |
| treatments | 91.4% | 91.4% | 91.4% | 32 | 0 | 3 | 3 |
| evac | 93.6% | 95.7% | 91.7% | 22 | 0 | 1 | 2 |
| vital_signs | 96.3% | 96.6% | 96.1% | 196 | 6 | 1 | 2 |

## Where the errors come from

- transcription: 30
- extraction: 26
- invented: 14

## Errors by group and stage

- identity / transcription: 10
- identity / extraction: 10
- medications / transcription: 9
- vital_signs / transcription: 5
- tourniquets / transcription: 5
- medications / extraction: 4
- medications / invented: 4
- mechanism / extraction: 3
- vital_signs / extraction: 3
- treatments / invented: 3
- mechanism / invented: 3
- tourniquets / extraction: 2
- evac / extraction: 2
- treatments / extraction: 2
- tourniquets / invented: 2
- vital_signs / invented: 1
- treatments / transcription: 1
- evac / invented: 1

## Every error

| file | field | stage | predicted | truth |
|---|---|---|---|---|
| aim | name | transcription | Carr, Jazz | Kaur, Jas |
| aim | mechanism_gsw | extraction | False | True |
| bwt | last4 | transcription |  | 5033 |
| bwt | tq_right_leg_time | extraction |  | 1235 |
| bwt | signs_1_time | invented | 1240 |  |
| bwt | signs_1_pulse | transcription | 130 carotid | 140 carotid |
| ihg | evac_urgent | extraction | False | True |
| ihg | date | transcription |  | 03-NOV-26 |
| ihg | unit | extraction | 1 unit | 1 Yorks |
| ihg | tq_right_leg_type | transcription |  | CAT |
| ihg | tq_right_leg_time | transcription | 1425 | 1424 |
| ihg | tq_left_leg_type | transcription |  | CAT |
| ihg | tq_left_leg_time | transcription | 1420 | 1422 |
| ihg | signs_1_pain | extraction |  | 9 Excruciating |
| ihg | other_med_1_route | transcription |  | IV |
| ihg | hypothermia_prevention | extraction | False | True |
| ihg | hypothermia_prevention_type | transcription |  | hypothermia prevention kit |
| ihg | first_responder_name | extraction | Jones | Jones, Sam |
| ihg | first_responder_last4 | transcription |  | 3318 |
| isa | other_med_1_route | transcription |  | IV |
| jql | first_responder_name | extraction | Dan, Kelly | Kelly, Dan |
| jql | first_responder_last4 | transcription |  | 2285 |
| liq | time | transcription | 1110 | 1100 |
| liq | tq_right_leg_time | extraction |  | 1106 |
| liq | signs_1_pulse | extraction | 140 carotid; no radial | 140 carotid |
| liq | first_responder_name | extraction | Owen, Rhys | Reece, Owen |
| mbs | evac_priority | invented | True | False |
| mbs | time | transcription |  | 0340 |
| mbs | unit | extraction | 4 Regiment Royal Artillery | 4th Regiment Royal Artillery |
| mbs | signs_1_pain | extraction | 0 None | 9 Excruciating |
| mbs | signs_2_time | transcription | 0450 | 0415 |
| mbs | blood_1_route | transcription |  | IV |
| mbs | splint | invented | True | False |
| oog | name | extraction | Davis, Rhys | Davies, Rhys |
| oog | date | transcription |  | 04-NOV-26 |
| oog | signs_2_time | transcription | 1015 | 0920 |
| oog | dressing_pressure | invented | True | False |
| oog | breathing_chest_seal | extraction | False | True |
| pbj | analgesic_1_time | extraction |  | 0855 |
| pbj | antibiotic_1_name | transcription | moxie | moxifloxacin |
| pbj | antibiotic_1_time | extraction |  | 0855 |
| pbj | other_med_1_name | transcription |  | TXA |
| pbj | other_med_1_dose | transcription |  | 1 g |
| pbj | other_med_1_time | extraction |  | 0900 |
| pbj | other_med_2_name | transcription |  | TXA |
| pbj | other_med_2_dose | transcription |  | 1 g |
| pbj | other_med_2_time | extraction |  | 0920 |
| qof | mechanism_artillery | invented | True | False |
| qof | first_responder_name | extraction | Hogan | Hogan, Ciara |
| roo | dressing_pressure | invented | True | False |
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
| xvw | unit | extraction | 1 Rifles | B Company, 1 Rifles |
| zas | mechanism_other | invented | True | False |
| zas | mechanism_other_text | invented | blast |  |
| zas | tq_right_arm_time | invented | 0748 |  |
| zas | tq_extremity | invented | True | False |
| zas | other_med_1_time | transcription | 0750 | 0755 |
