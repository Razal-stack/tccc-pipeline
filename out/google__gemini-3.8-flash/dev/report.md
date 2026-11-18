# google/gemini-3.8-flash on dev (25 cards)

Cards scored: 25 (25 with predictions)

F1 on filled fields:      95.0%  (precision 96.1%, recall 93.9%; 95% interval 91.9% to 97.3%)
Safety-critical fields:   94.3%  (precision 95.1%, recall 93.5%)
Invented values:          12 total, 0.48 per card
Injury boxes F1:          100.0%
Naive field accuracy:     98.6%  (an empty card scores 83.3%)

| Group | F1 | Precision | Recall | Correct | Wrong | Invented | Missed |
|---|---|---|---|---|---|---|---|
| medications | 93.0% | 92.6% | 93.5% | 87 | 3 | 4 | 3 |
| tourniquets | 93.5% | 96.7% | 90.6% | 29 | 1 | 0 | 2 |
| vital_signs | 94.3% | 95.5% | 93.1% | 190 | 1 | 8 | 13 |
| identity | 95.2% | 96.7% | 93.7% | 148 | 5 | 0 | 5 |
| mechanism | 96.2% | 100.0% | 92.6% | 25 | 0 | 0 | 2 |
| evac | 100.0% | 100.0% | 100.0% | 24 | 0 | 0 | 0 |
| treatments | 100.0% | 100.0% | 100.0% | 35 | 0 | 0 | 0 |

## Where the errors come from

- extraction: 23
- transcription: 12
- invented: 12

## Kinds of problem

- left blank: 25
- made up: 12
- digit off: 6
- name/unit spelling: 3
- wrong value: 1

## Errors by group and stage

- vital_signs / extraction: 12
- vital_signs / invented: 8
- identity / extraction: 6
- identity / transcription: 4
- medications / transcription: 4
- medications / invented: 4
- mechanism / extraction: 2
- tourniquets / transcription: 2
- medications / extraction: 2
- vital_signs / transcription: 2
- tourniquets / extraction: 1

## Every error

| file | field | stage | kind | predicted | truth |
|---|---|---|---|---|---|
| aim | name | extraction | left blank |  | Kaur, Jas |
| aim | mechanism_gsw | extraction | left blank | False | True |
| bwt | last4 | extraction | left blank |  | 5033 |
| bwt | signs_1_pulse | extraction | left blank |  | 140 carotid |
| ihg | tq_right_leg_time | transcription | digit off | 1425 | 1424 |
| ihg | tq_left_leg_time | extraction | left blank |  | 1422 |
| ihg | signs_1_pulse | extraction | left blank |  | 128 radial |
| ihg | analgesic_1_time | extraction | left blank |  | 1430 |
| ihg | first_responder_last4 | transcription | digit off | 3319 | 3318 |
| jql | first_responder_last4 | transcription | left blank |  | 2285 |
| liq | time | transcription | digit off | 1110 | 1100 |
| liq | first_responder_name | extraction | name/unit spelling | Rhys, Owen | Reece, Owen |
| mbs | signs_2_time | extraction | left blank |  | 0415 |
| mbs | signs_2_pulse | extraction | left blank |  | 116 radial |
| mbs | blood_1_route | transcription | wrong value | IO | IV |
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
| oog | signs_2_time | transcription | left blank |  | 0920 |
| pbj | other_med_1_dose | transcription | left blank |  | 1 g |
| pbj | other_med_2_dose | transcription | left blank |  | 1 g |
| roo | other_med_1_name | invented | made up | TXA |  |
| roo | other_med_1_dose | invented | made up | 2 g |  |
| roo | other_med_1_route | invented | made up | IV |  |
| roo | other_med_1_time | invented | made up | 1058 |  |
| uij | mechanism_mvc | extraction | left blank | False | True |
| vdi | time | extraction | left blank |  | 0715 |
| vdi | tq_left_leg_time | transcription | left blank |  | 0718 |
| vdi | signs_1_pulse | transcription | digit off | 160 | 130 |
| vdi | signs_1_resp_rate | invented | made up | 28 |  |
| xqh | date | extraction | left blank |  | 31-OCT-26 |
| xqh | signs_1_bp_diastolic | extraction | left blank |  | 76 |
| xqh | first_responder_name | extraction | name/unit spelling | Ahmed, Zayn | Ahmed, Zain |
| xvw | last4 | transcription | digit off | 7907 | 7007 |
| zas | blood_1_name | extraction | name/unit spelling | plasma | freeze-dried plasma |
| zas | other_med_1_time | transcription | digit off | 0750 | 0755 |
