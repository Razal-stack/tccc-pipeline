# z-ai/glm-5.3 on dev (25 cards)

Cards scored: 25 (25 with predictions)

F1 on filled fields:      91.2%  (precision 93.1%, recall 89.4%)
Safety-critical fields:   94.4%  (precision 95.7%, recall 93.2%)
Invented values:          12 total, 0.48 per card
Injury boxes F1:          87.0%
Naive field accuracy:     97.9%  (an empty card scores 83.3%)

| Group | F1 | Precision | Recall | Correct | Wrong | Invented | Missed |
|---|---|---|---|---|---|---|---|
| tourniquets | 82.0% | 86.2% | 78.1% | 25 | 4 | 0 | 3 |
| treatments | 82.9% | 82.9% | 82.9% | 29 | 0 | 6 | 6 |
| mechanism | 86.3% | 91.7% | 81.5% | 22 | 0 | 2 | 5 |
| identity | 86.6% | 89.8% | 83.5% | 132 | 15 | 0 | 11 |
| evac | 93.3% | 100.0% | 87.5% | 21 | 0 | 0 | 3 |
| medications | 94.6% | 94.6% | 94.6% | 88 | 1 | 4 | 4 |
| vital_signs | 96.3% | 97.0% | 95.6% | 195 | 6 | 0 | 3 |

## Where the errors come from

- extraction: 38
- transcription: 22
- invented: 12
- validation: 1

## Errors by group and stage

- identity / extraction: 16
- identity / transcription: 9
- vital_signs / transcription: 6
- treatments / invented: 6
- mechanism / extraction: 5
- treatments / extraction: 5
- tourniquets / extraction: 4
- medications / invented: 4
- evac / extraction: 3
- tourniquets / transcription: 3
- vital_signs / extraction: 3
- medications / transcription: 3
- medications / extraction: 2
- mechanism / invented: 2
- treatments / transcription: 1
- identity / validation: 1

## Every error

| file | field | stage | predicted | truth |
|---|---|---|---|---|
| aim | name | transcription | Carr, Jazz | Kaur, Jas |
| aim | mechanism_gsw | extraction | False | True |
| bwt | name | extraction | Byrne, Tom | Taylor |
| bwt | last4 | transcription | 1662 | 5033 |
| bwt | tq_right_leg_time | extraction |  | 1235 |
| bwt | signs_1_pulse | transcription | 130 carotid | 140 carotid |
| bwt | first_responder_name | extraction |  | Byrne, Tom |
| bwt | first_responder_last4 | extraction |  | 1662 |
| ihg | evac_urgent | extraction | False | True |
| ihg | unit | extraction |  | 1 Yorks |
| ihg | tq_right_leg_type | extraction |  | CAT |
| ihg | tq_right_leg_time | transcription | 1425 | 1424 |
| ihg | tq_left_leg_type | extraction |  | CAT |
| ihg | tq_left_leg_time | transcription | 1420 | 1422 |
| ihg | signs_1_pulse | extraction | 128 | 128 radial |
| ihg | signs_1_pain | extraction |  | 9 Excruciating |
| ihg | dressing_type | invented | QuikClot |  |
| ihg | other_med_1_route | extraction |  | IV |
| ihg | hypothermia_prevention | extraction | False | True |
| ihg | hypothermia_prevention_type | transcription |  | hypothermia prevention kit |
| ihg | first_responder_name | extraction |  | Jones, Sam |
| ihg | first_responder_last4 | transcription |  | 3318 |
| isa | other_med_1_route | extraction |  | IV |
| jql | dressing_type | extraction |  | burns dressings |
| jql | eye_shield | extraction | False | True |
| jql | first_responder_last4 | transcription |  | 2285 |
| jvq | unit | extraction | 2 Larc | 2 Lancs |
| liq | time | transcription | 1110 | 1100 |
| liq | tq_right_leg_time | extraction | 1102 | 1106 |
| liq | dressing_type | invented | Celox |  |
| liq | first_responder_name | extraction | Owen, Rhys | Reece, Owen |
| mbs | time | transcription | 0324 | 0340 |
| mbs | mechanism_blunt | extraction | False | True |
| mbs | mechanism_mvc | invented | True | False |
| mbs | signs_1_pain | extraction | 0 None | 9 Excruciating |
| mbs | signs_2_time | transcription | 0450 | 0415 |
| odw | evac_urgent | extraction | False | True |
| odw | gender_m | extraction | False | True |
| odw | mechanism_gsw | extraction | False | True |
| odw | dressing_pressure | extraction | False | True |
| odw | breathing_needle_d | extraction | False | True |
| oog | name | extraction | Davis, Rhys | Davies, Rhys |
| oog | date | transcription |  | 04-NOV-26 |
| oog | signs_2_time | transcription | 1015 | 0920 |
| pbj | other_med_1_dose | transcription |  | 1 g |
| pbj | other_med_2_dose | transcription |  | 1 g |
| qof | mechanism_artillery | invented | True | False |
| qof | first_responder_name | extraction | Hogan | Hogan, Ciara |
| roo | last4 | extraction | 42468 | 2468 |
| roo | dressing_pressure | invented | True | False |
| roo | other_med_1_name | invented | TXA |  |
| roo | other_med_1_dose | invented | 2 g |  |
| roo | other_med_1_route | invented | IV |  |
| roo | other_med_1_time | invented | 1058 |  |
| roo | first_responder_last4 | extraction | 43915 | 3915 |
| sfw | unit | validation |  | 2 Para |
| uij | last4 | extraction | 41212 | 1212 |
| uij | mechanism_mvc | extraction | False | True |
| vdi | evac_urgent | extraction | False | True |
| vdi | time | transcription |  | 0715 |
| vdi | mechanism_ied | extraction | False | True |
| vdi | tq_left_leg_time | transcription | 1115 | 0718 |
| vdi | signs_1_pulse | transcription |  | 130 |
| xqh | name | extraction | Murphy, Aoi | Murphy, Aoife |
| xqh | signs_1_bp_diastolic | transcription | 74 | 76 |
| xqh | first_responder_name | extraction | Ahmed, Zayn | Ahmed, Zain |
| xrp | signs_1_bp_systolic | transcription |  | 100 |
| xrp | dressing_type | invented | left leg only |  |
| xrp | airway_type | invented | surgical cric |  |
| xrp | breathing_type | invented | through the cric |  |
| xvw | last4 | transcription |  | 7007 |
| zas | unit | extraction | Two Squadron RAF Regiment | 2 Squadron RAF Regiment |
| zas | other_med_1_time | transcription | 0750 | 0755 |
