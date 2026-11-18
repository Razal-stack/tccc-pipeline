# mistralai/mistral-large-4-0 on dev (25 cards)

Cards scored: 25 (25 with predictions)

F1 on filled fields:      76.9%  (precision 95.8%, recall 64.2%)
Safety-critical fields:   77.0%  (precision 95.4%, recall 64.5%)
Invented values:          5 total, 0.20 per card
Injury boxes F1:          67.2%
Naive field accuracy:     93.9%  (an empty card scores 83.3%)

| Group | F1 | Precision | Recall | Correct | Wrong | Invented | Missed |
|---|---|---|---|---|---|---|---|
| tourniquets | 65.3% | 94.1% | 50.0% | 16 | 1 | 0 | 15 |
| medications | 65.3% | 88.9% | 51.6% | 48 | 2 | 4 | 43 |
| treatments | 71.4% | 95.2% | 57.1% | 20 | 0 | 1 | 15 |
| mechanism | 74.4% | 100.0% | 59.3% | 16 | 0 | 0 | 11 |
| identity | 78.7% | 96.3% | 66.5% | 105 | 4 | 0 | 49 |
| vital_signs | 82.5% | 97.3% | 71.6% | 146 | 4 | 0 | 54 |
| evac | 82.9% | 100.0% | 70.8% | 17 | 0 | 0 | 7 |

## Where the errors come from

- extraction: 179
- transcription: 26
- invented: 5

## Kinds of problem

- left blank: 194
- name/unit spelling: 5
- made up: 5
- digit off: 4
- wrong value: 2

## Errors by group and stage

- vital_signs / extraction: 49
- identity / extraction: 45
- medications / extraction: 39
- treatments / extraction: 15
- tourniquets / extraction: 13
- mechanism / extraction: 11
- vital_signs / transcription: 9
- identity / transcription: 8
- evac / extraction: 7
- medications / transcription: 6
- medications / invented: 4
- tourniquets / transcription: 3
- treatments / invented: 1

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
| mbs | signs_2_time | transcription | digit off | 0450 | 0415 |
| mbs | signs_2_pulse | transcription | wrong value | 160 radial | 116 radial |
| mbs | blood_1_route | transcription | left blank |  | IV |
| oog | date | transcription | left blank |  | 04-NOV-26 |
| oog | signs_2_time | transcription | digit off | 0915 | 0920 |
| pbj | antibiotic_1_name | transcription | name/unit spelling | moxy | moxifloxacin |
| pbj | antibiotic_1_dose | extraction | wrong value | 400 | 400 mg |
| pbj | other_med_1_dose | transcription | left blank |  | 1 g |
| pbj | other_med_2_dose | transcription | left blank |  | 1 g |
| qof | first_responder_name | extraction | name/unit spelling | Hogan, CRA | Hogan, Ciara |
| roo | dressing_pressure | invented | made up | True | False |
| roo | other_med_1_name | invented | made up | TXA |  |
| roo | other_med_1_dose | invented | made up | 2 g |  |
| roo | other_med_1_route | invented | made up | IV |  |
| roo | other_med_1_time | invented | made up | 1058 |  |
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
| xvw | evac_urgent | extraction | left blank | False | True |
| xvw | name | extraction | left blank |  | Young, Chloe |
| xvw | last4 | transcription | left blank |  | 7007 |
| xvw | gender_f | extraction | left blank | False | True |
| xvw | time | extraction | left blank |  | 1010 |
| xvw | service | extraction | left blank |  | Army |
| xvw | unit | extraction | left blank |  | B Company, 1 Rifles |
| xvw | mechanism_landmine | extraction | left blank | False | True |
| xvw | tq_right_leg_type | extraction | left blank |  | CAT |
| xvw | tq_right_leg_time | extraction | left blank |  | 1012 |
| xvw | signs_1_time | extraction | left blank |  | 1020 |
| xvw | signs_1_pulse | extraction | left blank |  | 116 radial |
| xvw | signs_1_bp_systolic | extraction | left blank |  | 108 |
| xvw | signs_1_bp_diastolic | extraction | left blank |  | 70 |
| xvw | signs_1_resp_rate | extraction | left blank |  | 24 |
| xvw | signs_1_spo2 | extraction | left blank |  | 96 |
| xvw | signs_1_avpu | extraction | left blank |  | A - Alert |
| xvw | signs_1_pain | extraction | left blank |  | 10 Unimaginable |
| xvw | tq_extremity | extraction | left blank | False | True |
| xvw | other_med_1_name | extraction | left blank |  | TXA |
| xvw | other_med_1_dose | extraction | left blank |  | 2 g |
| xvw | other_med_1_route | extraction | left blank |  | IV |
| xvw | other_med_1_time | extraction | left blank |  | 1025 |
| zas | battle_roster | extraction | left blank |  | CD1975 |
| zas | evac_urgent | extraction | left blank | False | True |
| zas | gender_f | extraction | left blank | False | True |
| zas | time | extraction | left blank |  | 0740 |
| zas | service | extraction | left blank |  | RAF |
| zas | unit | extraction | left blank |  | 2 Squadron RAF Regiment |
| zas | mechanism_artillery | extraction | left blank | False | True |
| zas | signs_1_time | extraction | left blank |  | 0750 |
| zas | signs_1_pulse | extraction | left blank |  | 132 radial |
| zas | signs_1_bp_systolic | extraction | left blank |  | 84 |
| zas | signs_1_bp_diastolic | extraction | left blank |  | 50 |
| zas | signs_1_resp_rate | extraction | left blank |  | 28 |
| zas | signs_1_spo2 | extraction | left blank |  | 95 |
| zas | signs_1_avpu | transcription | left blank |  | V - Verbal |
| zas | signs_1_pain | extraction | left blank |  | 8 Horrible |
| zas | signs_2_time | extraction | left blank |  | 0810 |
| zas | signs_2_pulse | extraction | left blank |  | 118 radial |
| zas | signs_2_bp_systolic | extraction | left blank |  | 96 |
| zas | signs_2_bp_diastolic | extraction | left blank |  | 60 |
| zas | signs_2_resp_rate | extraction | left blank |  | 24 |
| zas | signs_2_spo2 | extraction | left blank |  | 96 |
| zas | signs_2_avpu | transcription | left blank |  | V - Verbal |
| zas | tq_junctional | extraction | left blank | False | True |
| zas | dressing_hemostatic | extraction | left blank | False | True |
| zas | blood_1_name | extraction | left blank |  | freeze-dried plasma |
| zas | blood_1_volume | extraction | left blank |  | 1 unit |
| zas | blood_1_route | extraction | left blank |  | IV |
| zas | blood_1_time | extraction | left blank |  | 0800 |
| zas | other_med_1_name | extraction | left blank |  | TXA |
| zas | other_med_1_dose | extraction | left blank |  | 2 g |
| zas | other_med_1_route | extraction | left blank |  | IV |
| zas | other_med_1_time | transcription | left blank |  | 0755 |
