# deepseek/deepseek-v4.1-flash on dev (25 cards)

Cards scored: 25 (25 with predictions)

F1 on filled fields:      95.0%  (precision 95.6%, recall 94.4%)
Safety-critical fields:   95.9%  (precision 95.8%, recall 96.1%)
Invented values:          6 total, 0.24 per card
Injury boxes F1:          94.1%
Naive field accuracy:     98.9%  (an empty card scores 83.3%)

| Group | F1 | Precision | Recall | Correct | Wrong | Invented | Missed |
|---|---|---|---|---|---|---|---|
| tourniquets | 90.6% | 90.6% | 90.6% | 29 | 3 | 0 | 0 |
| identity | 93.2% | 94.8% | 91.8% | 145 | 8 | 0 | 5 |
| mechanism | 94.1% | 100.0% | 88.9% | 24 | 0 | 0 | 3 |
| medications | 94.1% | 93.6% | 94.6% | 88 | 2 | 4 | 3 |
| treatments | 94.3% | 94.3% | 94.3% | 33 | 1 | 1 | 1 |
| vital_signs | 97.1% | 97.1% | 97.1% | 198 | 5 | 1 | 1 |
| evac | 100.0% | 100.0% | 100.0% | 24 | 0 | 0 | 0 |

## Where the errors come from

- transcription: 20
- extraction: 12
- invented: 6

## Kinds of problem

- left blank: 13
- digit off: 10
- name/unit spelling: 6
- made up: 6
- wrong value: 3

## Errors by group and stage

- identity / transcription: 7
- identity / extraction: 6
- vital_signs / transcription: 6
- medications / transcription: 4
- medications / invented: 4
- mechanism / extraction: 3
- tourniquets / transcription: 3
- treatments / extraction: 2
- vital_signs / invented: 1
- medications / extraction: 1
- treatments / invented: 1

## Every error

| file | field | stage | kind | predicted | truth |
|---|---|---|---|---|---|
| aim | name | extraction | name/unit spelling | Carr, Jas | Kaur, Jas |
| aim | mechanism_gsw | extraction | left blank | False | True |
| bwt | last4 | transcription | left blank |  | 5033 |
| bwt | signs_1_time | invented | made up | 1240 |  |
| drm | eye_shield | extraction | left blank | False | True |
| ihg | tq_right_leg_time | transcription | digit off | 1425 | 1424 |
| ihg | tq_left_leg_time | transcription | digit off | 1420 | 1422 |
| ihg | signs_1_pulse | transcription | wrong value | 108 radial | 128 radial |
| ihg | analgesic_1_time | extraction | digit off | 1432 | 1430 |
| ihg | first_responder_name | extraction | name/unit spelling | Jones | Jones, Sam |
| ihg | first_responder_last4 | transcription | digit off | 3319 | 3318 |
| jql | dressing_type | extraction | wrong value | burns dressing | burns dressings |
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
| xvw | last4 | transcription | left blank |  | 7007 |
| zas | other_med_1_time | transcription | digit off | 0750 | 0755 |
