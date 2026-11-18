# qwen/qwen3.8-max-0902 on dev (25 cards)

Cards scored: 25 (25 with predictions)

F1 on filled fields:      87.7%  (precision 95.3%, recall 81.2%)
Safety-critical fields:   87.7%  (precision 95.4%, recall 81.1%)
Invented values:          6 total, 0.24 per card
Injury boxes F1:          82.4%
Naive field accuracy:     96.7%  (an empty card scores 83.3%)

| Group | F1 | Precision | Recall | Correct | Wrong | Invented | Missed |
|---|---|---|---|---|---|---|---|
| tourniquets | 81.4% | 88.9% | 75.0% | 24 | 3 | 0 | 5 |
| medications | 85.4% | 93.6% | 78.5% | 73 | 1 | 4 | 19 |
| identity | 86.7% | 94.1% | 80.4% | 127 | 8 | 0 | 23 |
| mechanism | 87.5% | 100.0% | 77.8% | 21 | 0 | 0 | 6 |
| vital_signs | 88.9% | 96.6% | 82.4% | 168 | 5 | 1 | 31 |
| treatments | 92.5% | 96.9% | 88.6% | 31 | 0 | 1 | 4 |
| evac | 93.3% | 100.0% | 87.5% | 21 | 0 | 0 | 3 |

## Where the errors come from

- extraction: 86
- transcription: 22
- invented: 6

## Kinds of problem

- left blank: 91
- digit off: 9
- name/unit spelling: 6
- made up: 6
- wrong value: 2

## Errors by group and stage

- vital_signs / extraction: 28
- identity / extraction: 24
- medications / extraction: 16
- vital_signs / transcription: 8
- identity / transcription: 7
- mechanism / extraction: 6
- tourniquets / extraction: 5
- medications / transcription: 4
- medications / invented: 4
- treatments / extraction: 4
- tourniquets / transcription: 3
- evac / extraction: 3
- vital_signs / invented: 1
- treatments / invented: 1

## Every error

| file | field | stage | kind | predicted | truth |
|---|---|---|---|---|---|
| aim | name | extraction | name/unit spelling | Carr, Jas | Kaur, Jas |
| aim | mechanism_gsw | extraction | left blank | False | True |
| bwt | last4 | transcription | left blank |  | 5033 |
| bwt | tq_right_leg_type | extraction | left blank |  | CAT |
| bwt | signs_1_time | invented | made up | 1240 |  |
| ihg | tq_right_leg_time | transcription | digit off | 1425 | 1424 |
| ihg | tq_left_leg_time | transcription | digit off | 1420 | 1422 |
| ihg | signs_1_pulse | transcription | wrong value | 108 radial | 128 radial |
| ihg | analgesic_1_time | extraction | digit off | 1432 | 1430 |
| ihg | first_responder_name | extraction | name/unit spelling | Jones | Jones, Sam |
| ihg | first_responder_last4 | transcription | digit off | 3319 | 3318 |
| jql | first_responder_last4 | transcription | left blank |  | 2285 |
| liq | time | transcription | digit off | 1110 | 1100 |
| liq | first_responder_name | extraction | name/unit spelling | Owen, Rhys | Reece, Owen |
| mbs | signs_2_time | transcription | digit off | 0450 | 0415 |
| mbs | signs_2_pulse | transcription | wrong value | 160 radial | 116 radial |
| mbs | blood_1_route | transcription | left blank |  | IV |
| oog | date | transcription | left blank |  | 04-NOV-26 |
| oog | signs_2_time | transcription | digit off | 0915 | 0920 |
| pbj | other_med_1_dose | transcription | left blank |  | 1 g |
| pbj | other_med_2_dose | transcription | left blank |  | 1 g |
| qof | first_responder_name | extraction | name/unit spelling | Hogan | Hogan, Ciara |
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
