# qwen/qwen4-max on dev (25 cards)

Cards scored: 25 (25 with predictions)

F1 on filled fields:      94.0%  (precision 94.7%, recall 93.4%)
Safety-critical fields:   93.9%  (precision 94.1%, recall 93.8%)
Invented values:          12 total, 0.48 per card
Injury boxes F1:          97.0%
Naive field accuracy:     98.5%  (an empty card scores 83.3%)

| Group | F1 | Precision | Recall | Correct | Wrong | Invented | Missed |
|---|---|---|---|---|---|---|---|
| tourniquets | 88.9% | 90.3% | 87.5% | 28 | 3 | 0 | 1 |
| identity | 93.2% | 94.8% | 91.8% | 145 | 8 | 0 | 5 |
| vital_signs | 93.9% | 94.1% | 93.6% | 191 | 5 | 7 | 8 |
| mechanism | 94.1% | 100.0% | 88.9% | 24 | 0 | 0 | 3 |
| medications | 94.1% | 93.6% | 94.6% | 88 | 2 | 4 | 3 |
| treatments | 98.6% | 97.2% | 100.0% | 35 | 0 | 1 | 0 |
| evac | 100.0% | 100.0% | 100.0% | 24 | 0 | 0 | 0 |

## Where the errors come from

- transcription: 20
- extraction: 18
- invented: 12

## Kinds of problem

- left blank: 20
- made up: 12
- digit off: 10
- name/unit spelling: 6
- wrong value: 2

## Errors by group and stage

- identity / transcription: 7
- vital_signs / extraction: 7
- vital_signs / invented: 7
- identity / extraction: 6
- vital_signs / transcription: 6
- medications / transcription: 4
- medications / invented: 4
- mechanism / extraction: 3
- tourniquets / transcription: 3
- tourniquets / extraction: 1
- medications / extraction: 1
- treatments / invented: 1

## Every error

| file | field | stage | kind | predicted | truth |
|---|---|---|---|---|---|
| aim | name | extraction | name/unit spelling | Carr, Jas | Kaur, Jas |
| aim | mechanism_gsw | extraction | left blank | False | True |
| bwt | last4 | transcription | left blank |  | 5033 |
| bwt | tq_right_leg_type | extraction | left blank |  | CAT |
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
| ojr | signs_1_time | extraction | left blank |  | 1410 |
| ojr | signs_1_bp_systolic | extraction | left blank |  | 120 |
| ojr | signs_1_bp_diastolic | extraction | left blank |  | 75 |
| ojr | signs_1_resp_rate | extraction | left blank |  | 20 |
| ojr | signs_1_spo2 | extraction | left blank |  | 97 |
| ojr | signs_1_avpu | extraction | left blank |  | A - Alert |
| ojr | signs_1_pain | extraction | left blank |  | 5 Very Distress |
| ojr | signs_2_time | invented | made up | 1410 |  |
| ojr | signs_2_bp_systolic | invented | made up | 120 |  |
| ojr | signs_2_bp_diastolic | invented | made up | 75 |  |
| ojr | signs_2_resp_rate | invented | made up | 20 |  |
| ojr | signs_2_spo2 | invented | made up | 97 |  |
| ojr | signs_2_avpu | invented | made up | A - Alert |  |
| ojr | signs_2_pain | invented | made up | 5 Very Distress |  |
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
| xvw | last4 | transcription | left blank |  | 7007 |
| zas | other_med_1_time | transcription | digit off | 0750 | 0755 |
