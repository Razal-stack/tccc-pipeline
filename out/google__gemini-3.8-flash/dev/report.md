# google/gemini-3.8-flash on dev (25 cards)

Cards scored: 25 (25 with predictions)

F1 on filled fields:      95.5%  (precision 97.5%, recall 93.5%; 95% interval 92.8% to 97.6%)
Safety-critical fields:   96.1%  (precision 97.4%, recall 94.9%)
Invented values:          4 total, 0.16 per card
Injury boxes F1:          97.0%
Naive field accuracy:     98.8%  (an empty card scores 83.3%)

| Group | F1 | Precision | Recall | Correct | Wrong | Invented | Missed |
|---|---|---|---|---|---|---|---|
| tourniquets | 90.6% | 90.6% | 90.6% | 29 | 3 | 0 | 0 |
| identity | 93.1% | 96.6% | 89.9% | 142 | 5 | 0 | 11 |
| mechanism | 94.1% | 100.0% | 88.9% | 24 | 0 | 0 | 3 |
| medications | 95.1% | 95.7% | 94.6% | 88 | 0 | 4 | 5 |
| vital_signs | 97.0% | 99.0% | 95.1% | 194 | 2 | 0 | 8 |
| evac | 100.0% | 100.0% | 100.0% | 24 | 0 | 0 | 0 |
| treatments | 100.0% | 100.0% | 100.0% | 35 | 0 | 0 | 0 |

## Where the errors come from

- extraction: 21
- transcription: 16
- invented: 4

## Kinds of problem

- left blank: 27
- digit off: 6
- made up: 4
- name/unit spelling: 3
- wrong value: 1

## Errors by group and stage

- identity / extraction: 11
- vital_signs / extraction: 5
- vital_signs / transcription: 5
- identity / transcription: 5
- medications / invented: 4
- mechanism / extraction: 3
- tourniquets / transcription: 3
- medications / transcription: 3
- medications / extraction: 2

## Every error

| file | field | stage | kind | predicted | truth |
|---|---|---|---|---|---|
| aim | name | extraction | name/unit spelling | Carr, Jas | Kaur, Jas |
| aim | mechanism_gsw | extraction | left blank | False | True |
| bwt | last4 | extraction | left blank |  | 5033 |
| bwt | signs_1_pulse | extraction | left blank |  | 140 carotid |
| ihg | tq_right_leg_time | transcription | digit off | 1425 | 1424 |
| ihg | tq_left_leg_time | transcription | digit off | 1420 | 1422 |
| ihg | signs_1_time | extraction | left blank |  | 1428 |
| ihg | signs_1_pulse | transcription | left blank |  | 128 radial |
| ihg | signs_1_bp_systolic | extraction | left blank |  | 92 |
| ihg | signs_1_bp_diastolic | extraction | left blank |  | 58 |
| ihg | analgesic_1_time | extraction | left blank |  | 1430 |
| ihg | first_responder_name | extraction | name/unit spelling | Jones | Jones, Sam |
| ihg | first_responder_last4 | transcription | digit off | 3319 | 3318 |
| jql | first_responder_last4 | transcription | left blank |  | 2285 |
| liq | time | transcription | digit off | 1110 | 1100 |
| liq | first_responder_name | extraction | left blank |  | Reece, Owen |
| mbs | time | extraction | left blank |  | 0340 |
| mbs | signs_2_time | transcription | digit off | 0450 | 0415 |
| mbs | signs_2_pulse | transcription | wrong value | 160 radial | 116 radial |
| mbs | blood_1_route | transcription | left blank |  | IV |
| oog | name | extraction | left blank |  | Davies, Rhys |
| oog | date | transcription | left blank |  | 04-NOV-26 |
| oog | signs_2_time | transcription | left blank |  | 0920 |
| pbj | other_med_1_dose | transcription | left blank |  | 1 g |
| pbj | other_med_2_dose | transcription | left blank |  | 1 g |
| qof | first_responder_name | extraction | name/unit spelling | Hogan | Hogan, Ciara |
| roo | other_med_1_name | invented | made up | TXA |  |
| roo | other_med_1_dose | invented | made up | 2 g |  |
| roo | other_med_1_route | invented | made up | IV |  |
| roo | other_med_1_time | invented | made up | 1058 |  |
| uij | mechanism_mvc | extraction | left blank | False | True |
| vdi | time | transcription | left blank |  | 0715 |
| vdi | mechanism_ied | extraction | left blank | False | True |
| vdi | tq_left_leg_time | transcription | digit off | 1715 | 0718 |
| vdi | signs_1_pulse | transcription | left blank |  | 130 |
| xqh | name | extraction | left blank |  | Murphy, Aoife |
| xqh | date | extraction | left blank |  | 31-OCT-26 |
| xqh | signs_1_bp_diastolic | extraction | left blank |  | 76 |
| xqh | first_responder_name | extraction | left blank |  | Ahmed, Zain |
| xrp | last4 | extraction | left blank |  | 1176 |
| zas | other_med_1_time | extraction | left blank |  | 0755 |
