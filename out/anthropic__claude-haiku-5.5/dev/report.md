# anthropic/claude-haiku-5.5 on dev (25 cards)

Cards scored: 25 (25 with predictions)

F1 on filled fields:      88.5%  (precision 89.8%, recall 87.3%)
Safety-critical fields:   92.3%  (precision 93.1%, recall 91.5%)
Invented values:          29 total, 1.16 per card
Injury boxes F1:          91.2%
Naive field accuracy:     97.0%  (an empty card scores 83.3%)

| Group | F1 | Precision | Recall | Correct | Wrong | Invented | Missed |
|---|---|---|---|---|---|---|---|
| tourniquets | 72.5% | 67.6% | 78.1% | 25 | 4 | 8 | 3 |
| treatments | 80.0% | 71.1% | 91.4% | 32 | 1 | 12 | 2 |
| identity | 82.6% | 87.9% | 77.8% | 123 | 16 | 1 | 19 |
| mechanism | 84.6% | 88.0% | 81.5% | 22 | 0 | 3 | 5 |
| medications | 91.7% | 94.3% | 89.2% | 83 | 1 | 4 | 9 |
| vital_signs | 95.5% | 96.5% | 94.6% | 193 | 6 | 1 | 5 |
| evac | 95.7% | 100.0% | 91.7% | 22 | 0 | 0 | 2 |

## Where the errors come from

- extraction: 50
- invented: 29
- transcription: 23

## Errors by group and stage

- identity / extraction: 26
- treatments / invented: 12
- identity / transcription: 9
- tourniquets / invented: 8
- vital_signs / transcription: 6
- medications / extraction: 6
- mechanism / extraction: 5
- vital_signs / extraction: 5
- tourniquets / extraction: 4
- medications / transcription: 4
- medications / invented: 4
- tourniquets / transcription: 3
- mechanism / invented: 3
- evac / extraction: 2
- treatments / extraction: 2
- vital_signs / invented: 1
- treatments / transcription: 1
- identity / invented: 1

## Every error

| file | field | stage | predicted | truth |
|---|---|---|---|---|
| aim | name | transcription | Carr, Jazz | Kaur, Jas |
| aim | last4 | extraction |  | 8336 |
| aim | mechanism_gsw | extraction | False | True |
| bwt | name | extraction | Byrne, Tom | Taylor |
| bwt | last4 | transcription | 1662 | 5033 |
| bwt | tq_right_leg_time | extraction |  | 1235 |
| bwt | signs_1_time | invented | 1240 |  |
| bwt | signs_1_pulse | transcription | 130 carotid | 140 carotid |
| bwt | tq_type | invented | CAT |  |
| bwt | first_responder_name | extraction |  | Byrne, Tom |
| bwt | first_responder_last4 | extraction |  | 1662 |
| cpx | name | extraction | Jack, Ellis | Ellis, Jack |
| cpx | signs_1_resp_rate | extraction |  | 18 |
| ihg | evac_urgent | extraction | False | True |
| ihg | unit | extraction |  | 1 Yorks |
| ihg | tq_right_leg_type | extraction |  | CAT |
| ihg | tq_right_leg_time | transcription | 1425 | 1424 |
| ihg | tq_left_leg_type | extraction |  | CAT |
| ihg | tq_left_leg_time | transcription | 1420 | 1422 |
| ihg | signs_1_pulse | extraction | 128 | 128 radial |
| ihg | signs_1_avpu | extraction |  | V - Verbal |
| ihg | signs_1_pain | extraction |  | 9 Excruciating |
| ihg | dressing_type | invented | QuikClot |  |
| ihg | other_med_1_route | extraction |  | IV |
| ihg | hypothermia_prevention | extraction | False | True |
| ihg | hypothermia_prevention_type | transcription |  | hypothermia prevention kit |
| ihg | first_responder_name | extraction |  | Jones, Sam |
| ihg | first_responder_last4 | transcription |  | 3318 |
| isa | tq_type | invented | CAT |  |
| isa | dressing_type | invented | hemostatic gauze |  |
| isa | other_med_1_route | extraction |  | IV |
| jql | mechanism_burn | extraction | False | True |
| jql | dressing_type | extraction | burns dressing | burns dressings |
| jql | first_responder_name | extraction | Dan, Kelly | Kelly, Dan |
| jql | first_responder_last4 | transcription |  | 2285 |
| jvq | unit | extraction | 2 Larc | 2 Lancs |
| jvq | tq_type | invented | CAT |  |
| jvq | dressing_type | invented | Celox |  |
| liq | last4 | invented | 3088 |  |
| liq | time | transcription | 1110 | 1100 |
| liq | tq_right_leg_time | extraction | 1102 | 1106 |
| liq | tq_type | invented | CAT |  |
| liq | dressing_type | invented | Celox |  |
| liq | first_responder_name | extraction | Owen, Rhys | Reece, Owen |
| lnf | last4 | extraction |  | 4480 |
| lnf | tq_type | invented | CAT |  |
| lnf | first_responder_last4 | extraction |  | 5593 |
| mbs | time | transcription |  | 0340 |
| mbs | mechanism_other | invented | True | False |
| mbs | mechanism_other_text | invented | struck by reversing Mastiff on gun line |  |
| mbs | signs_1_pain | extraction | 0 None | 9 Excruciating |
| mbs | signs_2_time | transcription | 0450 | 0415 |
| mbs | blood_1_route | extraction |  | IV |
| odw | unit | extraction |  | 45 Commando |
| odw | breathing_type | invented | needle decompression |  |
| oog | name | extraction | Davis, Rhys | Davies, Rhys |
| oog | date | transcription |  | 04-NOV-26 |
| oog | signs_2_time | transcription | 1015 | 0920 |
| oog | airway_type | invented | NPA |  |
| pbj | antibiotic_1_name | transcription |  | moxifloxacin |
| pbj | antibiotic_1_dose | extraction |  | 400 mg |
| pbj | antibiotic_1_route | extraction |  | PO |
| pbj | antibiotic_1_time | extraction |  | 0855 |
| pbj | other_med_1_dose | transcription |  | 1 g |
| pbj | other_med_2_dose | transcription |  | 1 g |
| qof | mechanism_artillery | invented | True | False |
| qof | mechanism_blunt | extraction | False | True |
| qof | first_responder_name | extraction | Hogan | Hogan, Ciara |
| roo | last4 | extraction |  | 2468 |
| roo | dressing_pressure | invented | True | False |
| roo | dressing_type | invented | hemostatic gauze |  |
| roo | other_med_1_name | invented | TXA |  |
| roo | other_med_1_dose | invented | 2 g |  |
| roo | other_med_1_route | invented | IV |  |
| roo | other_med_1_time | invented | 1058 |  |
| roo | first_responder_last4 | extraction |  | 3915 |
| sfw | last4 | extraction |  | 2771 |
| sfw | unit | extraction | Para | 2 Para |
| sfw | tq_type | invented | CAT |  |
| sfw | first_responder_last4 | extraction |  | 8841 |
| uij | last4 | extraction |  | 1212 |
| uij | mechanism_mvc | extraction | False | True |
| vdi | evac_urgent | extraction | False | True |
| vdi | time | transcription |  | 0715 |
| vdi | mechanism_ied | extraction | False | True |
| vdi | tq_left_leg_time | transcription | 1115 | 0718 |
| vdi | signs_1_pulse | transcription |  | 130 |
| xqh | name | extraction | Murphy, Aoi | Murphy, Aoife |
| xqh | unit | extraction | One Regiment RMP | 1 Regiment RMP |
| xqh | signs_1_bp_diastolic | transcription | 74 | 76 |
| xqh | first_responder_name | extraction | Zayn, Ahmed | Ahmed, Zain |
| xrp | signs_1_bp_systolic | transcription |  | 100 |
| xrp | dressing_type | invented | pressure |  |
| xrp | airway_type | invented | surgical cric |  |
| xrp | breathing_type | invented | oxygen |  |
| xvw | last4 | transcription |  | 7007 |
| xvw | unit | extraction | 1 Rifles | B Company, 1 Rifles |
| xvw | tq_type | invented | CAT |  |
| zas | unit | extraction | Two Squadron RAF Regiment | 2 Squadron RAF Regiment |
| zas | tq_type | invented | SAM |  |
| zas | dressing_type | invented | Celox |  |
| zas | other_med_1_time | transcription | 0750 | 0755 |
