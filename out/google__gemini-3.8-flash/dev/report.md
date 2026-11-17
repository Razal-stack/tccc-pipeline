# google/gemini-3.8-flash on dev (25 cards)

Cards scored: 25 (25 with predictions)

F1 on filled fields:      95.3%  (precision 95.9%, recall 94.8%)
Safety-critical fields:   96.1%  (precision 96.1%, recall 96.1%)
Invented values:          5 total, 0.20 per card
Injury boxes F1:          97.0%
Naive field accuracy:     99.0%  (an empty card scores 83.3%)

| Group | F1 | Precision | Recall | Correct | Wrong | Invented | Missed |
|---|---|---|---|---|---|---|---|
| tourniquets | 90.6% | 90.6% | 90.6% | 29 | 3 | 0 | 0 |
| identity | 93.2% | 94.8% | 91.8% | 145 | 8 | 0 | 5 |
| mechanism | 94.1% | 100.0% | 88.9% | 24 | 0 | 0 | 3 |
| medications | 94.1% | 93.6% | 94.6% | 88 | 2 | 4 | 3 |
| vital_signs | 97.3% | 97.5% | 97.1% | 198 | 5 | 0 | 1 |
| treatments | 98.6% | 97.2% | 100.0% | 35 | 0 | 1 | 0 |
| evac | 100.0% | 100.0% | 100.0% | 24 | 0 | 0 | 0 |

## Where the errors come from

- transcription: 20
- extraction: 10
- invented: 5

## Errors by group and stage

- identity / transcription: 7
- identity / extraction: 6
- vital_signs / transcription: 6
- medications / transcription: 4
- medications / invented: 4
- mechanism / extraction: 3
- tourniquets / transcription: 3
- medications / extraction: 1
- treatments / invented: 1

## Every error

| file | field | stage | predicted | truth |
|---|---|---|---|---|
| aim | name | extraction | Carr, Jas | Kaur, Jas |
| aim | mechanism_gsw | extraction | False | True |
| bwt | last4 | transcription |  | 5033 |
| ihg | tq_right_leg_time | transcription | 1425 | 1424 |
| ihg | tq_left_leg_time | transcription | 1420 | 1422 |
| ihg | signs_1_pulse | transcription | 108 radial | 128 radial |
| ihg | analgesic_1_time | extraction | 1432 | 1430 |
| ihg | first_responder_name | extraction | Jones | Jones, Sam |
| ihg | first_responder_last4 | transcription | 3319 | 3318 |
| jql | first_responder_last4 | transcription |  | 2285 |
| liq | time | transcription | 1110 | 1100 |
| liq | first_responder_name | extraction | Rhys, Owen | Reece, Owen |
| mbs | signs_2_time | transcription | 0450 | 0415 |
| mbs | signs_2_pulse | transcription | 160 radial | 116 radial |
| mbs | blood_1_route | transcription |  | IV |
| oog | date | transcription |  | 04-NOV-26 |
| oog | signs_2_time | transcription | 0915 | 0920 |
| pbj | other_med_1_dose | transcription |  | 1 g |
| pbj | other_med_2_dose | transcription |  | 1 g |
| qof | first_responder_name | extraction | Hogan | Hogan, Ciara |
| roo | dressing_pressure | invented | True | False |
| roo | other_med_1_name | invented | TXA |  |
| roo | other_med_1_dose | invented | 2 g |  |
| roo | other_med_1_route | invented | IV |  |
| roo | other_med_1_time | invented | 1058 |  |
| uij | mechanism_mvc | extraction | False | True |
| vdi | time | transcription |  | 0715 |
| vdi | mechanism_ied | extraction | False | True |
| vdi | tq_left_leg_time | transcription | 1715 | 0718 |
| vdi | signs_1_pulse | transcription |  | 130 |
| xqh | name | extraction | Murphy, Aoi | Murphy, Aoife |
| xqh | signs_1_bp_diastolic | transcription | 74 | 76 |
| xqh | first_responder_name | extraction | Ahmed, Zayn | Ahmed, Zain |
| xvw | last4 | transcription |  | 7007 |
| zas | other_med_1_time | transcription | 0750 | 0755 |
