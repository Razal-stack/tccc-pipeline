# openai/gpt-5.6-luna on dev (25 cards)

Cards scored: 25 (25 with predictions)

F1 on filled fields:      84.5%  (precision 95.2%, recall 75.9%)
Safety-critical fields:   84.5%  (precision 95.1%, recall 76.1%)
Invented values:          8 total, 0.32 per card
Injury boxes F1:          80.8%
Naive field accuracy:     95.7%  (an empty card scores 83.3%)

| Group | F1 | Precision | Recall | Correct | Wrong | Invented | Missed |
|---|---|---|---|---|---|---|---|
| medications | 78.0% | 90.1% | 68.8% | 64 | 2 | 5 | 27 |
| mechanism | 82.6% | 100.0% | 70.4% | 19 | 0 | 0 | 8 |
| tourniquets | 82.8% | 92.3% | 75.0% | 24 | 2 | 0 | 6 |
| identity | 84.5% | 95.2% | 75.9% | 120 | 6 | 0 | 32 |
| treatments | 86.2% | 93.3% | 80.0% | 28 | 0 | 2 | 7 |
| vital_signs | 87.0% | 97.0% | 78.9% | 161 | 4 | 1 | 39 |
| evac | 88.4% | 100.0% | 79.2% | 19 | 0 | 0 | 5 |

## Where the errors come from

- extraction: 114
- transcription: 24
- invented: 8

## Kinds of problem

- left blank: 124
- made up: 8
- digit off: 7
- name/unit spelling: 4
- wrong value: 3

## Errors by group and stage

- vital_signs / extraction: 35
- identity / extraction: 31
- medications / extraction: 23
- mechanism / extraction: 8
- vital_signs / transcription: 8
- identity / transcription: 7
- treatments / extraction: 7
- medications / transcription: 6
- medications / invented: 5
- evac / extraction: 5
- tourniquets / extraction: 5
- tourniquets / transcription: 3
- treatments / invented: 2
- vital_signs / invented: 1

## Every error

| file | field | stage | kind | predicted | truth |
|---|---|---|---|---|---|
| aim | name | extraction | name/unit spelling | Carr, Jas | Kaur, Jas |
| aim | mechanism_gsw | extraction | left blank | False | True |
| bwt | last4 | transcription | left blank |  | 5033 |
| bwt | signs_1_time | invented | made up | 1240 |  |
| ihg | tq_right_leg_time | transcription | digit off | 1425 | 1424 |
| ihg | tq_left_leg_time | transcription | digit off | 1420 | 1422 |
| ihg | signs_1_pulse | transcription | wrong value | 108 radial | 128 radial |
| ihg | analgesic_1_time | extraction | digit off | 1432 | 1430 |
| ihg | first_responder_name | extraction | name/unit spelling | Jones | Jones, Sam |
| ihg | first_responder_last4 | transcription | digit off | 3319 | 3318 |
| jql | mechanism_burn | extraction | left blank | False | True |
| jql | first_responder_last4 | transcription | left blank |  | 2285 |
| liq | time | transcription | digit off | 1110 | 1100 |
| liq | first_responder_name | extraction | name/unit spelling | Owen, Rhys | Reece, Owen |
| mbs | signs_2_time | transcription | digit off | 0450 | 0415 |
| mbs | signs_2_pulse | transcription | wrong value | 160 radial | 116 radial |
| mbs | blood_1_route | transcription | left blank |  | IV |
| oog | date | transcription | left blank |  | 04-NOV-26 |
| oog | signs_2_time | transcription | digit off | 0915 | 0920 |
| oog | dressing_other | invented | made up | True | False |
| oog | breathing_chest_seal | extraction | left blank | False | True |
| oog | antibiotic_1_dose | extraction | wrong value | 1 gram | 1 g |
| pbj | antibiotic_1_name | transcription | left blank |  | moxifloxacin |
| pbj | antibiotic_1_dose | extraction | left blank |  | 400 mg |
| pbj | antibiotic_1_route | transcription | left blank |  | PO |
| pbj | antibiotic_1_time | extraction | left blank |  | 0855 |
| pbj | other_med_1_dose | transcription | left blank |  | 1 g |
| pbj | other_med_1_route | invented | made up | PO |  |
| pbj | other_med_2_dose | transcription | left blank |  | 1 g |
| qof | first_responder_name | extraction | name/unit spelling | Hogan | Hogan, Ciara |
| roo | dressing_pressure | invented | made up | True | False |
| roo | other_med_1_name | invented | made up | TXA |  |
| roo | other_med_1_dose | invented | made up | 2 g |  |
| roo | other_med_1_route | invented | made up | IV |  |
| roo | other_med_1_time | invented | made up | 1058 |  |
| uij | mechanism_mvc | extraction | left blank | False | True |
| vdi | evac_urgent | extraction | left blank | False | True |
| vdi | time | transcription | left blank |  | 0715 |
| vdi | mechanism_ied | extraction | left blank | False | True |
| vdi | tq_left_leg_time | transcription | left blank |  | 0718 |
| vdi | signs_1_pulse | transcription | left blank |  | 130 |
| vdi | tq_extremity | extraction | left blank | False | True |
| xqh | evac_priority | extraction | left blank | False | True |
| xqh | name | extraction | left blank |  | Murphy, Aoife |
| xqh | last4 | extraction | left blank |  | 7258 |
| xqh | gender_f | extraction | left blank | False | True |
| xqh | date | extraction | left blank |  | 31-OCT-26 |
| xqh | time | extraction | left blank |  | 2310 |
| xqh | service | extraction | left blank |  | Army |
| xqh | unit | extraction | left blank |  | 1 Regiment RMP |
| xqh | mechanism_mvc | extraction | left blank | False | True |
| xqh | signs_1_time | extraction | left blank |  | 2320 |
| xqh | signs_1_pulse | extraction | left blank |  | 108 radial |
| xqh | signs_1_bp_systolic | extraction | left blank |  | 122 |
| xqh | signs_1_bp_diastolic | transcription | left blank |  | 76 |
| xqh | signs_1_resp_rate | extraction | left blank |  | 20 |
| xqh | signs_1_spo2 | extraction | left blank |  | 97 |
| xqh | signs_1_avpu | extraction | left blank |  | A - Alert |
| xqh | signs_1_pain | extraction | left blank |  | 9 Excruciating |
| xqh | dressing_pressure | extraction | left blank | False | True |
| xqh | analgesic_1_name | extraction | left blank |  | ketamine |
| xqh | analgesic_1_dose | extraction | left blank |  | 20 mg |
| xqh | analgesic_1_route | extraction | left blank |  | IV |
| xqh | analgesic_1_time | extraction | left blank |  | 2325 |
| xqh | splint | extraction | left blank | False | True |
| xqh | first_responder_name | extraction | left blank |  | Ahmed, Zain |
| xqh | first_responder_last4 | extraction | left blank |  | 1944 |
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
