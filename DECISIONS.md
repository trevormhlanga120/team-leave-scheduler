# Decisions

## 1. The 30% cap rounds down and is checked per working day

The system calculates the maximum number of people who may be away as
`floor(team_size * 0.3)`. For a team of 4, that means 1 person may be away on a
working day.

Alternatives considered:
- Round up, which would allow 2 people from a 4-person team to be away.
- Round to the nearest whole number.
- Apply the cap to the whole request range instead of each day.

Reasoning:
The rule says "on the same working day", so the check should happen per day.
Rounding down is the stricter interpretation and better protects small teams
from being understaffed.

## 2. Weekends and public holidays stay inside the request range but do not count

Employees may submit a date range that includes Saturdays, Sundays, or public
holidays. The request keeps the original start and end dates, but weekends and
public holidays are ignored when applying the team-cap rule.

Alternatives considered:
- Reject requests that include a weekend or holiday.
- Automatically split the request into separate working-day ranges.
- Rewrite the start or end date to the nearest working day.

Reasoning:
Managers usually think about leave as a date range, and rewriting ranges can be
surprising. Keeping the submitted range while ignoring non-working days makes the
API simple and preserves what the employee asked for.

## 3. Overlap is checked only against approved leave for the same employee

A request is invalid if it overlaps an already approved request for the same
employee. Pending requests may overlap each other, because a manager can reject
one later. The overlap check runs both when a request is submitted and again when
it is approved.

Alternatives considered:
- Block overlap with pending requests too.
- Allow overlap at submission and only validate during approval.
- Allow approved overlap when the overlap falls only on a weekend or holiday.

Reasoning:
The brief specifically says "existing approved request", so pending requests do
not block submission. Re-checking at approval prevents two pending requests from
both becoming approved after the order of decisions changes.
