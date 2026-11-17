# openai/gpt-5-nano on dev (25 cards)

Cards scored: 25 (25 with predictions)

F1 on filled fields:      85.4%  (precision 87.5%, recall 83.4%)
Safety-critical fields:   86.9%  (precision 88.1%, recall 85.6%)
Invented values:          15 total, 0.60 per card
Injury boxes F1:          75.3%
Naive field accuracy:     96.8%  (an empty card scores 83.3%)

| Group | F1 | Precision | Recall | Correct | Wrong | Invented | Missed |
|---|---|---|---|---|---|---|---|
| tourniquets | 78.7% | 82.8% | 75.0% | 24 | 4 | 1 | 4 |
| treatments | 82.0% | 96.2% | 71.4% | 25 | 0 | 1 | 10 |
| medications | 82.6% | 83.5% | 81.7% | 76 | 7 | 8 | 10 |
| mechanism | 83.0% | 84.6% | 81.5% | 22 | 0 | 4 | 5 |
| identity | 83.5% | 85.4% | 81.6% | 129 | 22 | 0 | 7 |
| vital_signs | 88.9% | 89.6% | 88.2% | 180 | 20 | 1 | 4 |
| evac | 95.7% | 100.0% | 91.7% | 22 | 0 | 0 | 2 |

## Where the errors come from

- extraction: 69
- transcription: 26
- invented: 15

## Errors by group and stage

- identity / extraction: 20
- vital_signs / extraction: 19
- identity / transcription: 9
- medications / extraction: 9
- treatments / extraction: 9
- medications / transcription: 8
- medications / invented: 8
- mechanism / extraction: 5
- vital_signs / transcription: 5
- tourniquets / extraction: 5
- mechanism / invented: 4
- tourniquets / transcription: 3
- evac / extraction: 2
- vital_signs / invented: 1
- treatments / transcription: 1
- treatments / invented: 1
- tourniquets / invented: 1

## Every error

| file | field | stage | predicted | truth |
|---|---|---|---|---|
| aim | name | transcription | Carr Jazz | Kaur, Jas |
| aim | mechanism_gsw | extraction | False | True |
| bwt | last4 | transcription |  | 5033 |
| bwt | signs_1_time | invented | 1240 |  |
| bwt | signs_1_pulse | transcription | 130 | 140 carotid |
| bwt | signs_1_avpu | extraction |  | P - Pain |
| cpx | name | extraction | Ellis Jack | Ellis, Jack |
| drm | signs_1_pulse | extraction | 110 | 110 radial |
| ihg | evac_urgent | extraction | False | True |
| ihg | gender_m | extraction | False | True |
| ihg | unit | extraction | 1 unit | 1 Yorks |
| ihg | tq_right_leg_type | extraction |  | CAT |
| ihg | tq_right_leg_time | transcription | 1425 | 1424 |
| ihg | tq_left_leg_type | extraction |  | CAT |
| ihg | tq_left_leg_time | transcription | 1420 | 1422 |
| ihg | signs_1_pulse | extraction | 128 | 128 radial |
| ihg | signs_1_pain | extraction |  | 9 Excruciating |
| ihg | analgesic_1_name | extraction | fentanyl lozenge | fentanyl |
| ihg | analgesic_1_route | transcription |  | OTFC |
| ihg | other_med_1_route | extraction |  | IV |
| ihg | hypothermia_prevention | extraction | False | True |
| ihg | hypothermia_prevention_type | transcription |  | hypothermia prevention kit |
| ihg | first_responder_name | extraction | Corporal Jones | Jones, Sam |
| ihg | first_responder_last4 | transcription | 1090 | 3318 |
| isa | gender_m | extraction | False | True |
| isa | signs_1_pulse | extraction | 120 | 120 radial |
| isa | signs_2_pulse | extraction | 108 | 108 radial |
| isa | other_med_1_route | extraction |  | IV |
| jql | mechanism_burn | extraction | False | True |
| jql | signs_1_pulse | extraction | 104 | 104 radial |
| jql | dressing_other | extraction | False | True |
| jql | dressing_type | extraction |  | burns dressings |
| jql | fluid_1_name | transcription | Hartmans | Hartmann's |
| jql | fluid_1_volume | extraction | 1 liter | 1 L |
| jql | combat_pill_pack | extraction | False | True |
| jql | hypothermia_prevention_type | extraction |  | blizzard blanket |
| jql | first_responder_name | extraction | Lance Corporal Kelly Dan | Kelly, Dan |
| jql | first_responder_last4 | transcription |  | 2285 |
| jvq | unit | extraction | 2 Larc. | 2 Lancs |
| jvq | signs_1_pulse | extraction | 126 | 126 radial |
| liq | time | transcription | 1110 | 1100 |
| liq | tq_right_leg_type | extraction | CAT high; CAT below | CAT |
| liq | tq_right_leg_time | extraction |  | 1106 |
| liq | first_responder_name | extraction | Rhys Owen | Reece, Owen |
| lnf | signs_1_pulse | extraction | 120 | 120 radial |
| mbs | time | transcription | 0324 | 0340 |
| mbs | mechanism_mvc | invented | True | False |
| mbs | signs_1_pulse | extraction | 130 | 130 radial |
| mbs | signs_1_pain | extraction | 0 None | 9 Excruciating |
| mbs | signs_2_time | transcription | 0450 | 0415 |
| mbs | signs_2_pulse | extraction | 116 | 116 radial |
| mbs | blood_1_route | extraction |  | IV |
| odw | unit | extraction | 45 commander | 45 Commando |
| oog | name | extraction | Davis, Rhys | Davies, Rhys |
| oog | date | transcription |  | 04-NOV-26 |
| oog | signs_2_time | transcription | 1015 | 0920 |
| oog | signs_2_pulse | extraction | 106 | 106 radial |
| oog | dressing_other | invented | True | False |
| oog | breathing_needle_d | extraction | False | True |
| oog | breathing_chest_seal | extraction | False | True |
| oog | antibiotic_1_dose | extraction | 1 gram | 1 g |
| pbj | analgesic_2_name | invented | moxie |  |
| pbj | analgesic_2_dose | invented | 400 mg |  |
| pbj | analgesic_2_route | invented | PO |  |
| pbj | analgesic_2_time | invented | 0855 |  |
| pbj | antibiotic_1_name | transcription |  | moxifloxacin |
| pbj | antibiotic_1_dose | extraction |  | 400 mg |
| pbj | antibiotic_1_route | extraction |  | PO |
| pbj | antibiotic_1_time | extraction |  | 0855 |
| pbj | other_med_1_name | transcription | TXL | TXA |
| pbj | other_med_1_dose | transcription |  | 1 g |
| pbj | other_med_2_name | transcription | TXL | TXA |
| pbj | other_med_2_dose | transcription |  | 1 g |
| qof | mechanism_artillery | invented | True | False |
| qof | signs_1_pulse | extraction | 116 | 116 radial |
| qof | splint | extraction | False | True |
| qof | hypothermia_prevention_type | extraction |  | HPMK |
| qof | first_responder_name | extraction | Lance Corporal Hogan | Hogan, Ciara |
| roo | name | extraction | Patel Nisha | Patel, Nisha |
| roo | signs_1_pulse | extraction | 116 | 116 radial |
| roo | signs_2_pulse | extraction | 104 | 104 radial |
| roo | other_med_1_name | invented | TXA |  |
| roo | other_med_1_dose | invented | 2 g |  |
| roo | other_med_1_route | invented | IV |  |
| roo | other_med_1_time | invented | 1058 |  |
| roo | first_responder_name | extraction | Doyle Mia | Doyle, Mia |
| sfw | last4 | extraction | 7712 | 2771 |
| sfw | unit | extraction | Para. | 2 Para |
| tup | signs_1_pulse | extraction | 84 | 84 radial |
| uij | name | extraction | Singh Priya | Singh, Priya |
| uij | mechanism_mvc | extraction | False | True |
| vdi | evac_urgent | extraction | False | True |
| vdi | time | transcription | 1115 | 0715 |
| vdi | mechanism_ied | extraction | False | True |
| vdi | tq_left_leg_time | transcription | 1115 | 0718 |
| vdi | signs_1_pulse | transcription |  | 130 |
| xqh | name | extraction | Murphy, Aoi | Murphy, Aoife |
| xqh | gender_f | extraction | False | True |
| xqh | signs_1_pulse | extraction | 108 | 108 radial |
| xqh | signs_1_bp_diastolic | transcription | 74 | 76 |
| xqh | first_responder_name | extraction | Ahmed Zayn | Ahmed, Zain |
| xrp | mechanism_ied | extraction | False | True |
| xrp | signs_1_avpu | extraction |  | P - Pain |
| xrp | first_responder_name | extraction | Hall Chris | Hall, Chris |
| xvw | last4 | transcription |  | 7007 |
| zas | mechanism_other | invented | True | False |
| zas | mechanism_other_text | invented | shrapnel wound |  |
| zas | tq_junctional | extraction | False | True |
| zas | tq_type | invented | SAM junctional |  |
| zas | other_med_1_time | transcription | 0750 | 0755 |
