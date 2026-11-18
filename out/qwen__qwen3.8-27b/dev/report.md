# qwen/qwen3.8-27b on dev (25 cards)

Cards scored: 25 (25 with predictions)

F1 on filled fields:      87.1%  (precision 97.0%, recall 79.1%)
Safety-critical fields:   87.1%  (precision 97.2%, recall 78.9%)
Invented values:          0 total, 0.00 per card
Injury boxes F1:          86.7%
Naive field accuracy:     96.5%  (an empty card scores 83.3%)

| Group | F1 | Precision | Recall | Correct | Wrong | Invented | Missed |
|---|---|---|---|---|---|---|---|
| tourniquets | 80.0% | 95.7% | 68.8% | 22 | 1 | 0 | 9 |
| mechanism | 85.1% | 100.0% | 74.1% | 20 | 0 | 0 | 7 |
| identity | 86.9% | 95.5% | 79.7% | 126 | 6 | 0 | 26 |
| vital_signs | 87.0% | 97.6% | 78.4% | 160 | 4 | 0 | 40 |
| medications | 87.7% | 96.2% | 80.6% | 75 | 3 | 0 | 15 |
| treatments | 90.6% | 100.0% | 82.9% | 29 | 0 | 0 | 6 |
| evac | 93.3% | 100.0% | 87.5% | 21 | 0 | 0 | 3 |

## Where the errors come from

- extraction: 94
- transcription: 26

## Kinds of problem

- left blank: 106
- name/unit spelling: 6
- digit off: 6
- wrong value: 2

## Errors by group and stage

- vital_signs / extraction: 37
- identity / extraction: 23
- medications / extraction: 12
- identity / transcription: 9
- mechanism / extraction: 7
- vital_signs / transcription: 7
- tourniquets / extraction: 6
- treatments / extraction: 6
- medications / transcription: 6
- tourniquets / transcription: 4
- evac / extraction: 3

## Every error

| file | field | stage | kind | predicted | truth |
|---|---|---|---|---|---|
| aim | name | extraction | name/unit spelling | Carr, Jas | Kaur, Jas |
| aim | mechanism_gsw | extraction | left blank | False | True |
| bwt | last4 | transcription | left blank |  | 5033 |
| bwt | tq_right_leg_type | extraction | left blank |  | CAT |
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
| isa | battle_roster | extraction | left blank |  | PK6009 |
| isa | evac_urgent | extraction | left blank | False | True |
| isa | gender_m | extraction | left blank | False | True |
| isa | time | transcription | left blank |  | 0650 |
| isa | service | extraction | left blank |  | Army |
| isa | unit | extraction | left blank |  | 1 Rifles |
| isa | mechanism_artillery | extraction | left blank | False | True |
| isa | tq_left_leg_type | extraction | left blank |  | CAT |
| isa | tq_left_leg_time | transcription | left blank |  | 0655 |
| isa | signs_1_time | extraction | left blank |  | 0700 |
| isa | signs_1_pulse | extraction | left blank |  | 120 radial |
| isa | signs_1_bp_systolic | extraction | left blank |  | 104 |
| isa | signs_1_bp_diastolic | extraction | left blank |  | 66 |
| isa | signs_1_resp_rate | extraction | left blank |  | 24 |
| isa | signs_1_spo2 | extraction | left blank |  | 95 |
| isa | signs_1_avpu | extraction | left blank |  | A - Alert |
| isa | signs_1_pain | extraction | left blank |  | 8 Horrible |
| isa | signs_2_time | extraction | left blank |  | 0715 |
| isa | signs_2_pulse | extraction | left blank |  | 108 radial |
| isa | signs_2_bp_systolic | extraction | left blank |  | 112 |
| isa | signs_2_bp_diastolic | extraction | left blank |  | 70 |
| isa | signs_2_resp_rate | extraction | left blank |  | 20 |
| isa | signs_2_spo2 | extraction | left blank |  | 97 |
| isa | signs_2_avpu | extraction | left blank |  | A - Alert |
| isa | signs_2_pain | extraction | left blank |  | 6 Intense |
| isa | tq_extremity | extraction | left blank | False | True |
| isa | dressing_hemostatic | extraction | left blank | False | True |
| isa | other_med_1_name | extraction | left blank |  | TXA |
| isa | other_med_1_dose | extraction | left blank |  | 2 g |
| isa | other_med_1_route | extraction | left blank |  | IV |
| isa | other_med_1_time | extraction | left blank |  | 0705 |
| jql | mechanism_burn | extraction | left blank | False | True |
| jql | first_responder_last4 | transcription | left blank |  | 2285 |
| liq | time | transcription | digit off | 1110 | 1100 |
| liq | first_responder_name | extraction | name/unit spelling | Rhys, Owen | Reece, Owen |
| mbs | signs_2_time | transcription | digit off | 0450 | 0415 |
| mbs | signs_2_pulse | transcription | wrong value | 160 radial | 116 radial |
| mbs | blood_1_route | transcription | left blank |  | IV |
| oog | date | transcription | left blank |  | 04-NOV-26 |
| oog | signs_2_time | transcription | digit off | 0915 | 0920 |
| pbj | antibiotic_1_name | transcription | name/unit spelling | mox | moxifloxacin |
| pbj | antibiotic_1_dose | extraction | wrong value | 400 | 400 mg |
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
| xvw | last4 | transcription | left blank |  | 7007 |
| zas | other_med_1_time | transcription | digit off | 0750 | 0755 |
