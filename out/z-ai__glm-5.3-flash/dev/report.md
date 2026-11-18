# z-ai/glm-5.3-flash on dev (25 cards)

Cards scored: 25 (25 with predictions)

F1 on filled fields:      93.5%  (precision 96.1%, recall 91.1%)
Safety-critical fields:   94.4%  (precision 96.2%, recall 92.7%)
Invented values:          4 total, 0.16 per card
Injury boxes F1:          96.0%
Naive field accuracy:     98.4%  (an empty card scores 83.3%)

| Group | F1 | Precision | Recall | Correct | Wrong | Invented | Missed |
|---|---|---|---|---|---|---|---|
| identity | 91.4% | 95.2% | 88.0% | 139 | 7 | 0 | 12 |
| medications | 91.8% | 93.3% | 90.3% | 84 | 2 | 4 | 7 |
| tourniquets | 92.1% | 93.5% | 90.6% | 29 | 2 | 0 | 1 |
| mechanism | 94.1% | 100.0% | 88.9% | 24 | 0 | 0 | 3 |
| treatments | 94.1% | 97.0% | 91.4% | 32 | 1 | 0 | 2 |
| vital_signs | 95.2% | 97.4% | 93.1% | 190 | 5 | 0 | 9 |
| evac | 100.0% | 100.0% | 100.0% | 24 | 0 | 0 | 0 |

## Where the errors come from

- transcription: 21
- validation: 17
- extraction: 13
- invented: 4

## Kinds of problem

- left blank: 34
- digit off: 9
- name/unit spelling: 5
- made up: 4
- wrong value: 3

## Errors by group and stage

- identity / extraction: 7
- identity / transcription: 7
- vital_signs / transcription: 7
- vital_signs / validation: 7
- identity / validation: 5
- medications / transcription: 4
- medications / validation: 4
- medications / invented: 4
- mechanism / extraction: 3
- tourniquets / transcription: 3
- treatments / extraction: 2
- medications / extraction: 1
- treatments / validation: 1

## Every error

| file | field | stage | kind | predicted | truth |
|---|---|---|---|---|---|
| aim | name | extraction | name/unit spelling | Carr, Jas | Kaur, Jas |
| aim | mechanism_gsw | extraction | left blank | False | True |
| bwt | last4 | transcription | left blank |  | 5033 |
| drm | eye_shield | extraction | left blank | False | True |
| ihg | tq_right_leg_time | transcription | digit off | 1425 | 1424 |
| ihg | tq_left_leg_time | transcription | digit off | 1420 | 1422 |
| ihg | signs_1_pulse | transcription | wrong value | 108 radial | 128 radial |
| ihg | analgesic_1_time | extraction | digit off | 1432 | 1430 |
| ihg | first_responder_name | extraction | name/unit spelling | Jones | Jones, Sam |
| ihg | first_responder_last4 | transcription | digit off | 3319 | 3318 |
| jql | dressing_type | extraction | wrong value | burn dressings | burns dressings |
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
| qof | name | validation | left blank |  | Wright |
| qof | last4 | validation | left blank |  | 6604 |
| qof | date | validation | left blank |  | 05-NOV-26 |
| qof | time | extraction | left blank |  | 0530 |
| qof | unit | validation | left blank |  | 1 Royal Irish |
| qof | signs_1_time | validation | left blank |  | 0550 |
| qof | signs_1_pulse | validation | left blank |  | 116 radial |
| qof | signs_1_bp_systolic | validation | left blank |  | 108 |
| qof | signs_1_bp_diastolic | validation | left blank |  | 70 |
| qof | signs_1_resp_rate | validation | left blank |  | 22 |
| qof | signs_1_spo2 | validation | left blank |  | 95 |
| qof | signs_1_avpu | transcription | left blank |  | V - Verbal |
| qof | signs_1_pain | validation | left blank |  | 9 Excruciating |
| qof | analgesic_1_name | validation | left blank |  | morphine |
| qof | analgesic_1_dose | validation | left blank |  | 10 mg |
| qof | analgesic_1_route | validation | left blank |  | IM |
| qof | analgesic_1_time | validation | left blank |  | 0558 |
| qof | hypothermia_prevention_type | validation | left blank |  | HPMK |
| qof | first_responder_name | extraction | left blank |  | Hogan, Ciara |
| qof | first_responder_last4 | validation | left blank |  | 4772 |
| roo | other_med_1_name | invented | made up | TXA |  |
| roo | other_med_1_dose | invented | made up | 2 g |  |
| roo | other_med_1_route | invented | made up | IV |  |
| roo | other_med_1_time | invented | made up | 1058 |  |
| uij | mechanism_mvc | extraction | left blank | False | True |
| vdi | time | transcription | left blank |  | 0715 |
| vdi | mechanism_ied | extraction | left blank | False | True |
| vdi | tq_left_leg_time | transcription | left blank |  | 0718 |
| vdi | signs_1_pulse | transcription | left blank |  | 130 |
| xqh | name | extraction | name/unit spelling | Murphy, Aoi | Murphy, Aoife |
| xqh | signs_1_bp_diastolic | transcription | digit off | 74 | 76 |
| xqh | first_responder_name | extraction | name/unit spelling | Ahmed, Zayn | Ahmed, Zain |
| xvw | last4 | transcription | left blank |  | 7007 |
| zas | other_med_1_time | transcription | digit off | 0750 | 0755 |
