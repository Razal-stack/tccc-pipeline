# google/gemini-4-argon on dev (25 cards)

Cards scored: 25 (25 with predictions)

F1 on filled fields:      95.5%  (precision 96.1%, recall 94.9%)
Safety-critical fields:   96.1%  (precision 96.1%, recall 96.1%)
Invented values:          5 total, 0.20 per card
Injury boxes F1:          100.0%
Naive field accuracy:     99.0%  (an empty card scores 83.3%)

| Group | F1 | Precision | Recall | Correct | Wrong | Invented | Missed |
|---|---|---|---|---|---|---|---|
| tourniquets | 90.6% | 90.6% | 90.6% | 29 | 3 | 0 | 0 |
| identity | 93.6% | 94.8% | 92.4% | 146 | 7 | 1 | 5 |
| mechanism | 94.1% | 100.0% | 88.9% | 24 | 0 | 0 | 3 |
| medications | 94.1% | 93.6% | 94.6% | 88 | 2 | 4 | 3 |
| vital_signs | 97.3% | 97.5% | 97.1% | 198 | 5 | 0 | 1 |
| evac | 100.0% | 100.0% | 100.0% | 24 | 0 | 0 | 0 |
| treatments | 100.0% | 100.0% | 100.0% | 35 | 0 | 0 | 0 |

## Where the errors come from

- transcription: 20
- extraction: 9
- invented: 5

## Kinds of problem

- left blank: 12
- digit off: 10
- name/unit spelling: 5
- made up: 5
- wrong value: 2

## Errors by group and stage

- identity / transcription: 7
- vital_signs / transcription: 6
- identity / extraction: 5
- medications / transcription: 4
- medications / invented: 4
- mechanism / extraction: 3
- tourniquets / transcription: 3
- identity / invented: 1
- medications / extraction: 1

## Every error

| file | field | stage | kind | predicted | truth |
|---|---|---|---|---|---|
| aim | name | extraction | name/unit spelling | Carr, Jas | Kaur, Jas |
| aim | mechanism_gsw | extraction | left blank | False | True |
| bwt | last4 | transcription | left blank |  | 5033 |
| bwt | service | invented | made up | Army |  |
| ihg | tq_right_leg_time | transcription | digit off | 1425 | 1424 |
| ihg | tq_left_leg_time | transcription | digit off | 1420 | 1422 |
| ihg | signs_1_pulse | transcription | wrong value | 108 radial | 128 radial |
| ihg | analgesic_1_time | extraction | digit off | 1432 | 1430 |
| ihg | first_responder_name | extraction | name/unit spelling | Jones | Jones, Sam |
| ihg | first_responder_last4 | transcription | digit off | 3319 | 3318 |
| jql | first_responder_last4 | transcription | left blank |  | 2285 |
| liq | time | transcription | digit off | 1110 | 1100 |
| liq | first_responder_name | extraction | name/unit spelling | Rhys, Owen | Reece, Owen |
| mbs | signs_2_time | transcription | digit off | 0450 | 0415 |
| mbs | signs_2_pulse | transcription | wrong value | 160 radial | 116 radial |
| mbs | blood_1_route | transcription | left blank |  | IV |
| oog | date | transcription | left blank |  | 04-NOV-26 |
| oog | signs_2_time | transcription | digit off | 0915 | 0920 |
| pbj | other_med_1_dose | transcription | left blank |  | 1 g |
| pbj | other_med_2_dose | transcription | left blank |  | 1 g |
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
