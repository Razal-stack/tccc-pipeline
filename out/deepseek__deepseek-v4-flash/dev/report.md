# deepseek/deepseek-v4-flash on dev (25 cards)

Cards scored: 25 (25 with predictions)

F1 on filled fields:      88.1%  (precision 91.5%, recall 85.0%)
Safety-critical fields:   90.5%  (precision 92.9%, recall 88.2%)
Invented values:          22 total, 0.88 per card
Injury boxes F1:          77.4%
Naive field accuracy:     96.8%  (an empty card scores 83.3%)

| Group | F1 | Precision | Recall | Correct | Wrong | Invented | Missed |
|---|---|---|---|---|---|---|---|
| tourniquets | 69.8% | 71.0% | 68.8% | 22 | 3 | 6 | 7 |
| treatments | 79.4% | 89.3% | 71.4% | 25 | 0 | 3 | 10 |
| mechanism | 80.8% | 84.0% | 77.8% | 21 | 0 | 4 | 6 |
| identity | 85.8% | 89.7% | 82.3% | 130 | 13 | 2 | 15 |
| medications | 88.4% | 90.9% | 86.0% | 80 | 2 | 6 | 11 |
| evac | 90.9% | 100.0% | 83.3% | 20 | 0 | 0 | 4 |
| vital_signs | 94.7% | 96.9% | 92.6% | 189 | 5 | 1 | 10 |

## Where the errors come from

- extraction: 62
- transcription: 24
- invented: 22

## Errors by group and stage

- identity / extraction: 19
- vital_signs / extraction: 10
- identity / transcription: 9
- treatments / extraction: 9
- medications / extraction: 9
- mechanism / extraction: 6
- medications / invented: 6
- tourniquets / invented: 6
- tourniquets / extraction: 5
- vital_signs / transcription: 5
- tourniquets / transcription: 5
- medications / transcription: 4
- evac / extraction: 4
- mechanism / invented: 4
- treatments / invented: 3
- identity / invented: 2
- vital_signs / invented: 1
- treatments / transcription: 1

## Every error

| file | field | stage | predicted | truth |
|---|---|---|---|---|
| aim | name | transcription | Carr, Jazz | Kaur, Jas |
| aim | mechanism_gsw | extraction | False | True |
| bwt | last4 | transcription |  | 5033 |
| bwt | tq_right_leg_time | extraction |  | 1235 |
| bwt | signs_1_time | invented | 1240 |  |
| bwt | signs_1_pulse | transcription | 130 carotid | 140 carotid |
| drm | time | extraction | 1340 | 1330 |
| ihg | unit | extraction |  | 1 Yorks |
| ihg | tq_right_leg_type | transcription |  | CAT |
| ihg | tq_right_leg_time | transcription | 1425 | 1424 |
| ihg | tq_left_leg_type | transcription |  | CAT |
| ihg | tq_left_leg_time | transcription | 1420 | 1422 |
| ihg | signs_1_pain | extraction |  | 9 Excruciating |
| ihg | other_med_1_route | transcription |  | IV |
| ihg | hypothermia_prevention | extraction | False | True |
| ihg | hypothermia_prevention_type | transcription |  | hypothermia prevention kit |
| ihg | first_responder_name | extraction | Jones | Jones, Sam |
| ihg | first_responder_last4 | transcription | 3319 | 3318 |
| jql | battle_roster | extraction |  | MT7703 |
| jql | evac_priority | extraction | False | True |
| jql | gender_m | extraction | False | True |
| jql | time | extraction |  | 1640 |
| jql | service | extraction |  | Army |
| jql | unit | extraction |  | Queen's Royal Hussars |
| jql | mechanism_burn | extraction | False | True |
| jql | mechanism_rpg | extraction | False | True |
| jql | signs_1_time | extraction |  | 1650 |
| jql | signs_1_pulse | extraction |  | 104 radial |
| jql | signs_1_bp_systolic | extraction |  | 128 |
| jql | signs_1_bp_diastolic | extraction |  | 80 |
| jql | signs_1_resp_rate | extraction |  | 22 |
| jql | signs_1_spo2 | extraction |  | 97 |
| jql | signs_1_avpu | extraction |  | A - Alert |
| jql | signs_1_pain | extraction |  | 6 Intense |
| jql | dressing_other | extraction | False | True |
| jql | dressing_type | extraction |  | burns dressings |
| jql | fluid_1_name | extraction |  | Hartmann's |
| jql | fluid_1_volume | extraction |  | 1 L |
| jql | fluid_1_route | extraction |  | IV |
| jql | fluid_1_time | extraction |  | 1655 |
| jql | analgesic_1_name | extraction |  | ketamine |
| jql | analgesic_1_dose | extraction |  | 20 mg |
| jql | analgesic_1_route | extraction |  | IV |
| jql | analgesic_1_time | extraction |  | 1658 |
| jql | combat_pill_pack | extraction | False | True |
| jql | eye_shield | extraction | False | True |
| jql | eye_shield_right | extraction | False | True |
| jql | hypothermia_prevention | extraction | False | True |
| jql | hypothermia_prevention_type | extraction |  | blizzard blanket |
| jql | first_responder_name | extraction |  | Kelly, Dan |
| jql | first_responder_last4 | transcription |  | 2285 |
| jvq | evac_urgent | extraction | False | True |
| liq | time | transcription | 1110 | 1100 |
| liq | tq_right_leg_time | extraction | 1102 | 1106 |
| liq | first_responder_name | extraction | Owen, Rhys | Reece, Owen |
| lnf | first_responder_last4 | extraction |  | 5593 |
| mbs | time | transcription | 0324 | 0340 |
| mbs | mechanism_mvc | invented | True | False |
| mbs | signs_1_pain | extraction | 0 None | 9 Excruciating |
| mbs | signs_2_time | transcription | 0450 | 0415 |
| mbs | splint | invented | True | False |
| oog | name | extraction | Davis, Rhys | Davies, Rhys |
| oog | date | transcription | NOV-26 | 04-NOV-26 |
| oog | signs_2_time | transcription | 1015 | 0920 |
| oog | breathing_chest_seal | extraction | False | True |
| oog | antibiotic_1_dose | extraction | 1 gram | 1 g |
| pbj | other_med_1_dose | transcription |  | 1 g |
| pbj | other_med_1_route | invented | IV |  |
| pbj | other_med_2_dose | transcription |  | 1 g |
| pbj | other_med_2_route | invented | IV |  |
| qof | service | invented | Army |  |
| qof | mechanism_artillery | invented | True | False |
| qof | first_responder_name | extraction | Hogan | Hogan, Ciara |
| roo | dressing_pressure | invented | True | False |
| roo | other_med_1_name | invented | TXA |  |
| roo | other_med_1_dose | invented | 2 g |  |
| roo | other_med_1_route | invented | IV |  |
| roo | other_med_1_time | invented | 1058 |  |
| sfw | last4 | extraction |  | 2771 |
| sfw | tq_right_leg_type | extraction |  | CAT |
| sfw | tq_right_leg_time | extraction |  | 0518 |
| sfw | tq_left_leg_type | invented | CAT |  |
| sfw | tq_left_leg_time | invented | 0518 |  |
| uij | allergies | invented | NKA |  |
| uij | mechanism_mvc | extraction | False | True |
| vdi | evac_urgent | extraction | False | True |
| vdi | time | transcription |  | 0715 |
| vdi | mechanism_ied | extraction | False | True |
| vdi | tq_left_leg_time | transcription |  | 0718 |
| vdi | signs_1_pulse | transcription |  | 130 |
| vdi | tq_extremity | extraction | False | True |
| xqh | name | extraction | Murphy, Aoi | Murphy, Aoife |
| xqh | signs_1_bp_diastolic | transcription | 74 | 76 |
| xqh | first_responder_name | extraction | Zayn, Ahmed | Ahmed, Zain |
| xrp | dressing_other | invented | True | False |
| xrp | first_responder_last4 | extraction |  | 4409 |
| xvw | evac_urgent | extraction | False | True |
| xvw | last4 | transcription |  | 7007 |
| xvw | gender_f | extraction | False | True |
| xvw | unit | extraction | 1 Rifles | B Company, 1 Rifles |
| xvw | mechanism_landmine | extraction | False | True |
| zas | mechanism_other | invented | True | False |
| zas | mechanism_other_text | invented | shrapnel |  |
| zas | tq_right_leg_type | invented | SAM junctional |  |
| zas | tq_right_leg_time | invented | 0748 |  |
| zas | tq_extremity | invented | True | False |
| zas | tq_type | invented | SAM junctional |  |
| zas | other_med_1_time | transcription | 0750 | 0755 |
