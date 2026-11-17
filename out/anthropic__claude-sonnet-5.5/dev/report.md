# anthropic/claude-sonnet-5.5 on dev (25 cards)

Cards scored: 25 (25 with predictions)

F1 on filled fields:      90.9%  (precision 93.4%, recall 88.5%)
Safety-critical fields:   93.8%  (precision 95.6%, recall 92.1%)
Invented values:          13 total, 0.52 per card
Injury boxes F1:          92.4%
Naive field accuracy:     97.7%  (an empty card scores 83.3%)

| Group | F1 | Precision | Recall | Correct | Wrong | Invented | Missed |
|---|---|---|---|---|---|---|---|
| tourniquets | 80.6% | 83.3% | 78.1% | 25 | 4 | 1 | 3 |
| mechanism | 83.0% | 84.6% | 81.5% | 22 | 0 | 4 | 5 |
| identity | 85.9% | 91.4% | 81.0% | 128 | 12 | 0 | 18 |
| treatments | 88.9% | 86.5% | 91.4% | 32 | 1 | 4 | 2 |
| medications | 91.7% | 94.3% | 89.2% | 83 | 1 | 4 | 9 |
| evac | 95.7% | 100.0% | 91.7% | 22 | 0 | 0 | 2 |
| vital_signs | 96.5% | 97.5% | 95.6% | 195 | 5 | 0 | 4 |

## Where the errors come from

- extraction: 42
- transcription: 24
- invented: 13

## Errors by group and stage

- identity / extraction: 21
- identity / transcription: 9
- vital_signs / transcription: 6
- mechanism / extraction: 5
- medications / extraction: 5
- medications / transcription: 5
- tourniquets / extraction: 4
- treatments / invented: 4
- mechanism / invented: 4
- medications / invented: 4
- tourniquets / transcription: 3
- vital_signs / extraction: 3
- evac / extraction: 2
- treatments / extraction: 2
- treatments / transcription: 1
- tourniquets / invented: 1

## Every error

| file | field | stage | predicted | truth |
|---|---|---|---|---|
| aim | name | transcription | Carr, Jazz | Kaur, Jas |
| aim | last4 | extraction |  | 8336 |
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
| ihg | signs_1_avpu | extraction |  | V - Verbal |
| ihg | signs_1_pain | extraction |  | 9 Excruciating |
| ihg | other_med_1_route | extraction |  | IV |
| ihg | hypothermia_prevention | extraction | False | True |
| ihg | hypothermia_prevention_type | transcription |  | hypothermia prevention kit |
| ihg | first_responder_name | extraction |  | Jones, Sam |
| ihg | first_responder_last4 | transcription |  | 3318 |
| isa | other_med_1_route | extraction |  | IV |
| jql | dressing_type | extraction | Burns dressing | burns dressings |
| jql | first_responder_last4 | transcription |  | 2285 |
| jvq | unit | extraction | 2 Larc | 2 Lancs |
| jvq | dressing_type | invented | Celox |  |
| liq | time | transcription | 1110 | 1100 |
| liq | tq_right_leg_time | extraction | 1102 | 1106 |
| liq | dressing_type | invented | Celox |  |
| liq | first_responder_name | extraction | Owen, Rhys | Reece, Owen |
| lnf | last4 | extraction |  | 4480 |
| lnf | first_responder_last4 | extraction |  | 5593 |
| mbs | time | transcription |  | 0340 |
| mbs | mechanism_blunt | extraction | False | True |
| mbs | mechanism_other | invented | True | False |
| mbs | mechanism_other_text | invented | Hit by reversing Mastiff on gun line |  |
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
| qof | mechanism_blunt | extraction | False | True |
| qof | mechanism_other | invented | True | False |
| qof | mechanism_other_text | invented | Building collapse, trapped under rubble |  |
| qof | first_responder_name | extraction | Hogan | Hogan, Ciara |
| roo | last4 | extraction |  | 2468 |
| roo | other_med_1_name | invented | TXA |  |
| roo | other_med_1_dose | invented | 2 g |  |
| roo | other_med_1_route | invented | IV |  |
| roo | other_med_1_time | invented | 1058 |  |
| roo | first_responder_last4 | extraction |  | 3915 |
| sfw | last4 | extraction |  | 2771 |
| sfw | unit | extraction | Para | 2 Para |
| sfw | first_responder_last4 | extraction |  | 8841 |
| uij | last4 | extraction |  | 1212 |
| uij | mechanism_mvc | extraction | False | True |
| vdi | evac_urgent | extraction | False | True |
| vdi | time | transcription |  | 0715 |
| vdi | mechanism_ied | extraction | False | True |
| vdi | tq_left_leg_time | transcription | 1115 | 0718 |
| vdi | signs_1_pulse | transcription |  | 130 |
| xqh | name | extraction | Murphy, Aoi | Murphy, Aoife |
| xqh | signs_1_bp_diastolic | transcription | 74 | 76 |
| xqh | first_responder_name | extraction | Zayn, Ahmed | Ahmed, Zain |
| xrp | signs_1_bp_systolic | transcription |  | 100 |
| xrp | airway_type | invented | surgical cric |  |
| xvw | last4 | transcription |  | 7007 |
| xvw | unit | extraction | 1 Rifles | B Company, 1 Rifles |
| zas | tq_type | invented | SAM junctional |  |
| zas | dressing_type | invented | Celox |  |
| zas | other_med_1_time | transcription | 0750 | 0755 |
