# qwen/qwen3.8-flash on dev (25 cards)

Cards scored: 25 (25 with predictions)

F1 on filled fields:      70.5%  (precision 97.8%, recall 55.1%)
Safety-critical fields:   72.4%  (precision 98.5%, recall 57.2%)
Invented values:          0 total, 0.00 per card
Injury boxes F1:          61.9%
Naive field accuracy:     92.5%  (an empty card scores 83.3%)

| Group | F1 | Precision | Recall | Correct | Wrong | Invented | Missed |
|---|---|---|---|---|---|---|---|
| treatments | 60.0% | 100.0% | 42.9% | 15 | 0 | 0 | 20 |
| tourniquets | 68.0% | 94.4% | 53.1% | 17 | 1 | 0 | 14 |
| mechanism | 68.3% | 100.0% | 51.9% | 14 | 0 | 0 | 13 |
| identity | 68.8% | 95.5% | 53.8% | 85 | 4 | 0 | 69 |
| medications | 69.4% | 98.0% | 53.8% | 50 | 1 | 0 | 42 |
| vital_signs | 73.8% | 99.2% | 58.8% | 120 | 1 | 0 | 83 |
| evac | 76.9% | 100.0% | 62.5% | 15 | 0 | 0 | 9 |

## Where the errors come from

- extraction: 232
- transcription: 25

## Kinds of problem

- left blank: 250
- name/unit spelling: 4
- digit off: 3

## Errors by group and stage

- vital_signs / extraction: 77
- identity / extraction: 64
- medications / extraction: 37
- treatments / extraction: 20
- mechanism / extraction: 13
- tourniquets / extraction: 12
- evac / extraction: 9
- identity / transcription: 9
- vital_signs / transcription: 7
- medications / transcription: 6
- tourniquets / transcription: 3

## Every error

| file | field | stage | kind | predicted | truth |
|---|---|---|---|---|---|
| aim | name | extraction | name/unit spelling | Carr, Jas | Kaur, Jas |
| aim | mechanism_gsw | extraction | left blank | False | True |
| bwt | evac_urgent | extraction | left blank | False | True |
| bwt | name | extraction | left blank |  | Taylor |
| bwt | last4 | transcription | left blank |  | 5033 |
| bwt | gender_m | extraction | left blank | False | True |
| bwt | time | extraction | left blank |  | 1220 |
| bwt | unit | extraction | left blank |  | 2 Yorks |
| bwt | mechanism_ied | extraction | left blank | False | True |
| bwt | tq_right_leg_type | extraction | left blank |  | CAT |
| bwt | tq_right_leg_time | extraction | left blank |  | 1235 |
| bwt | signs_1_pulse | extraction | left blank |  | 140 carotid |
| bwt | signs_1_resp_rate | extraction | left blank |  | 30 |
| bwt | signs_1_avpu | extraction | left blank |  | P - Pain |
| bwt | tq_extremity | extraction | left blank | False | True |
| bwt | other_med_1_name | extraction | left blank |  | TXA |
| bwt | other_med_1_dose | extraction | left blank |  | 2 g |
| bwt | other_med_1_route | extraction | left blank |  | IO |
| bwt | other_med_1_time | extraction | left blank |  | 1238 |
| bwt | first_responder_name | extraction | left blank |  | Byrne, Tom |
| bwt | first_responder_last4 | extraction | left blank |  | 1662 |
| ihg | battle_roster | extraction | left blank |  | JS4417 |
| ihg | evac_urgent | extraction | left blank | False | True |
| ihg | gender_m | extraction | left blank | False | True |
| ihg | date | transcription | left blank |  | 03-NOV-26 |
| ihg | time | extraction | left blank |  | 1420 |
| ihg | service | extraction | left blank |  | Army |
| ihg | unit | extraction | left blank |  | 1 Yorks |
| ihg | mechanism_ied | extraction | left blank | False | True |
| ihg | tq_right_leg_type | extraction | left blank |  | CAT |
| ihg | tq_right_leg_time | transcription | left blank |  | 1424 |
| ihg | tq_left_leg_type | extraction | left blank |  | CAT |
| ihg | tq_left_leg_time | transcription | left blank |  | 1422 |
| ihg | signs_1_time | extraction | left blank |  | 1428 |
| ihg | signs_1_pulse | transcription | left blank |  | 128 radial |
| ihg | signs_1_bp_systolic | extraction | left blank |  | 92 |
| ihg | signs_1_bp_diastolic | extraction | left blank |  | 58 |
| ihg | signs_1_resp_rate | extraction | left blank |  | 26 |
| ihg | signs_1_spo2 | extraction | left blank |  | 94 |
| ihg | signs_1_avpu | transcription | left blank |  | V - Verbal |
| ihg | signs_1_pain | extraction | left blank |  | 9 Excruciating |
| ihg | tq_extremity | extraction | left blank | False | True |
| ihg | dressing_hemostatic | extraction | left blank | False | True |
| ihg | analgesic_1_name | extraction | left blank |  | fentanyl |
| ihg | analgesic_1_dose | extraction | left blank |  | 800 mcg |
| ihg | analgesic_1_route | transcription | left blank |  | OTFC |
| ihg | analgesic_1_time | extraction | left blank |  | 1430 |
| ihg | other_med_1_name | extraction | left blank |  | TXA |
| ihg | other_med_1_dose | extraction | left blank |  | 2 g |
| ihg | other_med_1_route | extraction | left blank |  | IV |
| ihg | other_med_1_time | extraction | left blank |  | 1435 |
| ihg | hypothermia_prevention | extraction | left blank | False | True |
| ihg | hypothermia_prevention_type | extraction | left blank |  | hypothermia prevention kit |
| ihg | first_responder_name | extraction | left blank |  | Jones, Sam |
| ihg | first_responder_last4 | transcription | left blank |  | 3318 |
| jql | battle_roster | extraction | left blank |  | MT7703 |
| jql | evac_priority | extraction | left blank | False | True |
| jql | gender_m | extraction | left blank | False | True |
| jql | time | extraction | left blank |  | 1640 |
| jql | service | extraction | left blank |  | Army |
| jql | unit | extraction | left blank |  | Queen's Royal Hussars |
| jql | mechanism_burn | extraction | left blank | False | True |
| jql | mechanism_rpg | extraction | left blank | False | True |
| jql | signs_1_time | extraction | left blank |  | 1650 |
| jql | signs_1_pulse | extraction | left blank |  | 104 radial |
| jql | signs_1_bp_systolic | extraction | left blank |  | 128 |
| jql | signs_1_bp_diastolic | extraction | left blank |  | 80 |
| jql | signs_1_resp_rate | extraction | left blank |  | 22 |
| jql | signs_1_spo2 | extraction | left blank |  | 97 |
| jql | signs_1_avpu | extraction | left blank |  | A - Alert |
| jql | signs_1_pain | extraction | left blank |  | 6 Intense |
| jql | dressing_other | extraction | left blank | False | True |
| jql | dressing_type | extraction | left blank |  | burns dressings |
| jql | fluid_1_name | extraction | left blank |  | Hartmann's |
| jql | fluid_1_volume | extraction | left blank |  | 1 L |
| jql | fluid_1_route | extraction | left blank |  | IV |
| jql | fluid_1_time | extraction | left blank |  | 1655 |
| jql | analgesic_1_name | extraction | left blank |  | ketamine |
| jql | analgesic_1_dose | extraction | left blank |  | 20 mg |
| jql | analgesic_1_route | extraction | left blank |  | IV |
| jql | analgesic_1_time | extraction | left blank |  | 1658 |
| jql | combat_pill_pack | extraction | left blank | False | True |
| jql | eye_shield | extraction | left blank | False | True |
| jql | eye_shield_right | extraction | left blank | False | True |
| jql | hypothermia_prevention | extraction | left blank | False | True |
| jql | hypothermia_prevention_type | extraction | left blank |  | blizzard blanket |
| jql | first_responder_name | extraction | left blank |  | Kelly, Dan |
| jql | first_responder_last4 | transcription | left blank |  | 2285 |
| liq | battle_roster | extraction | left blank |  | LH3088 |
| liq | evac_urgent | extraction | left blank | False | True |
| liq | name | extraction | left blank |  | Hughes |
| liq | gender_m | extraction | left blank | False | True |
| liq | time | transcription | left blank |  | 1100 |
| liq | mechanism_landmine | extraction | left blank | False | True |
| liq | tq_right_leg_type | extraction | left blank |  | CAT |
| liq | tq_right_leg_time | extraction | left blank |  | 1106 |
| liq | signs_1_time | extraction | left blank |  | 1115 |
| liq | signs_1_pulse | extraction | left blank |  | 140 carotid |
| liq | signs_1_resp_rate | extraction | left blank |  | 32 |
| liq | signs_1_avpu | extraction | left blank |  | P - Pain |
| liq | tq_extremity | extraction | left blank | False | True |
| liq | dressing_hemostatic | extraction | left blank | False | True |
| liq | blood_1_name | extraction | left blank |  | whole blood |
| liq | blood_1_volume | extraction | left blank |  | 1 unit |
| liq | blood_1_route | extraction | left blank |  | IO |
| liq | blood_1_time | extraction | left blank |  | 1120 |
| liq | first_responder_name | extraction | left blank |  | Reece, Owen |
| liq | first_responder_last4 | extraction | left blank |  | 9044 |
| mbs | evac_urgent | extraction | left blank | False | True |
| mbs | name | extraction | left blank |  | Shaw, Ben |
| mbs | last4 | extraction | left blank |  | 1505 |
| mbs | gender_m | extraction | left blank | False | True |
| mbs | date | extraction | left blank |  | 30-OCT-26 |
| mbs | time | extraction | left blank |  | 0340 |
| mbs | service | extraction | left blank |  | Army |
| mbs | unit | extraction | left blank |  | 4th Regiment Royal Artillery |
| mbs | mechanism_blunt | extraction | left blank | False | True |
| mbs | signs_1_time | extraction | left blank |  | 0348 |
| mbs | signs_1_pulse | extraction | left blank |  | 130 radial |
| mbs | signs_1_bp_systolic | extraction | left blank |  | 88 |
| mbs | signs_1_bp_diastolic | extraction | left blank |  | 54 |
| mbs | signs_1_resp_rate | extraction | left blank |  | 26 |
| mbs | signs_1_spo2 | extraction | left blank |  | 96 |
| mbs | signs_1_avpu | extraction | left blank |  | A - Alert |
| mbs | signs_1_pain | extraction | left blank |  | 9 Excruciating |
| mbs | signs_2_time | transcription | left blank |  | 0415 |
| mbs | signs_2_pulse | transcription | left blank |  | 116 radial |
| mbs | signs_2_bp_systolic | extraction | left blank |  | 98 |
| mbs | signs_2_bp_diastolic | extraction | left blank |  | 62 |
| mbs | signs_2_resp_rate | extraction | left blank |  | 22 |
| mbs | signs_2_spo2 | extraction | left blank |  | 97 |
| mbs | signs_2_avpu | extraction | left blank |  | A - Alert |
| mbs | signs_2_pain | extraction | left blank |  | 6 Intense |
| mbs | blood_1_name | extraction | left blank |  | whole blood |
| mbs | blood_1_volume | extraction | left blank |  | 1 unit |
| mbs | blood_1_route | transcription | left blank |  | IV |
| mbs | blood_1_time | extraction | left blank |  | 0405 |
| mbs | analgesic_1_name | extraction | left blank |  | fentanyl |
| mbs | analgesic_1_dose | extraction | left blank |  | 800 mcg |
| mbs | analgesic_1_route | transcription | left blank |  | OTFC |
| mbs | analgesic_1_time | extraction | left blank |  | 0350 |
| mbs | first_responder_name | extraction | left blank |  | Lyle, Owen |
| mbs | first_responder_last4 | extraction | left blank |  | 6052 |
| ojr | battle_roster | extraction | left blank |  | TB2251 |
| ojr | evac_priority | extraction | left blank | False | True |
| ojr | gender_m | extraction | left blank | False | True |
| ojr | date | extraction | left blank |  | 02-NOV-26 |
| ojr | time | extraction | left blank |  | 1400 |
| ojr | mechanism_gsw | extraction | left blank | False | True |
| ojr | tq_left_leg_type | extraction | left blank |  | SOFTT-W |
| ojr | tq_left_leg_time | extraction | left blank |  | 1405 |
| ojr | signs_1_time | extraction | left blank |  | 1410 |
| ojr | signs_1_pulse | extraction | left blank |  | 110 radial |
| ojr | signs_1_bp_systolic | extraction | left blank |  | 120 |
| ojr | signs_1_bp_diastolic | extraction | left blank |  | 75 |
| ojr | signs_1_resp_rate | extraction | left blank |  | 20 |
| ojr | signs_1_spo2 | extraction | left blank |  | 97 |
| ojr | signs_1_avpu | extraction | left blank |  | A - Alert |
| ojr | signs_1_pain | extraction | left blank |  | 5 Very Distress |
| ojr | tq_extremity | extraction | left blank | False | True |
| oog | evac_urgent | extraction | left blank | False | True |
| oog | name | extraction | left blank |  | Davies, Rhys |
| oog | last4 | extraction | left blank |  | 2906 |
| oog | gender_m | extraction | left blank | False | True |
| oog | date | transcription | left blank |  | 04-NOV-26 |
| oog | time | extraction | left blank |  | 0905 |
| oog | service | extraction | left blank |  | Army |
| oog | unit | extraction | left blank |  | 2 Platoon, B Company |
| oog | allergies | transcription | left blank |  | NKA |
| oog | mechanism_gsw | extraction | left blank | False | True |
| oog | signs_1_time | extraction | left blank |  | 0910 |
| oog | signs_1_pulse | extraction | left blank |  | 118 radial |
| oog | signs_1_resp_rate | extraction | left blank |  | 30 |
| oog | signs_1_spo2 | extraction | left blank |  | 88 |
| oog | signs_1_avpu | extraction | left blank |  | A - Alert |
| oog | signs_1_pain | extraction | left blank |  | 7 Very Intense |
| oog | signs_2_time | transcription | left blank |  | 0920 |
| oog | signs_2_pulse | extraction | left blank |  | 106 radial |
| oog | signs_2_bp_systolic | extraction | left blank |  | 110 |
| oog | signs_2_bp_diastolic | extraction | left blank |  | 70 |
| oog | signs_2_resp_rate | extraction | left blank |  | 24 |
| oog | signs_2_spo2 | extraction | left blank |  | 95 |
| oog | signs_2_avpu | extraction | left blank |  | A - Alert |
| oog | airway_npa | extraction | left blank | False | True |
| oog | breathing_o2 | extraction | left blank | False | True |
| oog | breathing_needle_d | extraction | left blank | False | True |
| oog | breathing_chest_seal | extraction | left blank | False | True |
| oog | antibiotic_1_name | extraction | left blank |  | ertapenem |
| oog | antibiotic_1_dose | extraction | left blank |  | 1 g |
| oog | antibiotic_1_route | extraction | left blank |  | IV |
| oog | antibiotic_1_time | extraction | left blank |  | 0925 |
| oog | first_responder_name | extraction | left blank |  | Nash, Kieran |
| oog | first_responder_last4 | extraction | left blank |  | 5019 |
| pbj | other_med_1_dose | transcription | left blank |  | 1 g |
| pbj | other_med_2_dose | transcription | left blank |  | 1 g |
| qof | first_responder_name | extraction | name/unit spelling | Hogan | Hogan, Ciara |
| roo | evac_urgent | extraction | left blank | False | True |
| roo | name | extraction | left blank |  | Patel, Nisha |
| roo | last4 | extraction | left blank |  | 2468 |
| roo | gender_f | extraction | left blank | False | True |
| roo | time | extraction | left blank |  | 1045 |
| roo | service | extraction | left blank |  | Army |
| roo | unit | extraction | left blank |  | 1 Royal Anglian |
| roo | mechanism_gsw | extraction | left blank | False | True |
| roo | signs_1_time | extraction | left blank |  | 1052 |
| roo | signs_1_pulse | extraction | left blank |  | 116 radial |
| roo | signs_1_bp_systolic | extraction | left blank |  | 104 |
| roo | signs_1_bp_diastolic | extraction | left blank |  | 68 |
| roo | signs_1_resp_rate | extraction | left blank |  | 24 |
| roo | signs_1_spo2 | extraction | left blank |  | 95 |
| roo | signs_1_avpu | extraction | left blank |  | A - Alert |
| roo | signs_1_pain | extraction | left blank |  | 6 Intense |
| roo | signs_2_time | extraction | left blank |  | 1105 |
| roo | signs_2_pulse | extraction | left blank |  | 104 radial |
| roo | signs_2_bp_systolic | extraction | left blank |  | 112 |
| roo | signs_2_bp_diastolic | extraction | left blank |  | 72 |
| roo | signs_2_resp_rate | extraction | left blank |  | 20 |
| roo | signs_2_spo2 | extraction | left blank |  | 97 |
| roo | signs_2_avpu | extraction | left blank |  | A - Alert |
| roo | dressing_hemostatic | extraction | left blank | False | True |
| roo | breathing_o2 | extraction | left blank | False | True |
| roo | first_responder_name | extraction | left blank |  | Doyle, Mia |
| roo | first_responder_last4 | extraction | left blank |  | 3915 |
| uij | mechanism_mvc | extraction | left blank | False | True |
| vdi | time | transcription | left blank |  | 0715 |
| vdi | mechanism_ied | extraction | left blank | False | True |
| vdi | tq_left_leg_time | transcription | digit off | 1715 | 0718 |
| vdi | signs_1_pulse | transcription | left blank |  | 130 |
| xqh | name | extraction | name/unit spelling | Murphy, Aoi | Murphy, Aoife |
| xqh | signs_1_bp_diastolic | transcription | digit off | 74 | 76 |
| xqh | first_responder_name | extraction | name/unit spelling | Ahmed, Zayn | Ahmed, Zain |
| xrp | evac_urgent | extraction | left blank | False | True |
| xrp | name | extraction | left blank |  | Evans |
| xrp | last4 | extraction | left blank |  | 1176 |
| xrp | gender_m | extraction | left blank | False | True |
| xrp | date | extraction | left blank |  | 01-NOV-26 |
| xrp | time | extraction | left blank |  | 0820 |
| xrp | unit | extraction | left blank |  | 1 Royal Welsh |
| xrp | mechanism_ied | extraction | left blank | False | True |
| xrp | signs_1_time | extraction | left blank |  | 0838 |
| xrp | signs_1_pulse | extraction | left blank |  | 124 radial |
| xrp | signs_1_bp_systolic | extraction | left blank |  | 100 |
| xrp | signs_1_bp_diastolic | extraction | left blank |  | 64 |
| xrp | signs_1_resp_rate | extraction | left blank |  | 24 |
| xrp | signs_1_spo2 | extraction | left blank |  | 92 |
| xrp | signs_1_avpu | extraction | left blank |  | P - Pain |
| xrp | dressing_pressure | extraction | left blank | False | True |
| xrp | airway_cric | extraction | left blank | False | True |
| xrp | breathing_o2 | extraction | left blank | False | True |
| xrp | analgesic_1_name | extraction | left blank |  | ketamine |
| xrp | analgesic_1_dose | extraction | left blank |  | 50 mg |
| xrp | analgesic_1_route | extraction | left blank |  | IV |
| xrp | analgesic_1_time | extraction | left blank |  | 0835 |
| xrp | first_responder_name | extraction | left blank |  | Hall, Chris |
| xrp | first_responder_last4 | extraction | left blank |  | 4409 |
| xvw | last4 | transcription | left blank |  | 7007 |
| zas | other_med_1_time | transcription | digit off | 0750 | 0755 |
