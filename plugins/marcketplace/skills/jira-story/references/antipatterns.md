# Antipatterns to cut from every AC sentence

These patterns came out of real corrected tickets; the examples here are re-fictionalised
against Northwind Logistics (Freight Ops, project `FLT`, per `profiles/example.md`). Each
one is a pattern that shipped and got cut. Re-check every sentence you write against this
list before presenting or pushing, on every ticket, every time. Fixing it once on old text
does not make it happen automatically on new text written later in the same session.

## 1. Fluffy noun-phrase labels

A clinical-sounding label that stands in for plainly describing the actual case.

- **Before:** "Cross-carrier duplicate-link behaviour is undefined."
- **After:** "If carrier B tries to link a depot account carrier A already holds, [the actual
  resolution, once decided]."

The label sounds precise. It adds no information; it abstracts the scenario away instead of
stating it.

## 2. Trailing self-justification clauses

A clause after a requirement that explains or defends the AC's own scope, rather than
stating a fact the reader needs.

- **Before:** "...tracked separately in FLT-212; this AC doesn't attempt to solve it, only
  to state the default case."
- **After:** "...tracked separately in FLT-212." Stop there. The reader does not need to be
  told what the AC is not trying to do.

## 3. Restating a guarantee in its negative form

Saying the same thing twice, once as what happens and once as what does not, when the first
already implies the second.

- **Before:** "...the cancelled load is visibly noted, never silently re-priced, and never
  silently dropped from the total with no explanation."
- **After:** "...the cancelled load is visibly noted." If it is visibly noted, "silently
  dropped" is already ruled out.

## 4. Inherited-parity phrasing used before parity is confirmed

"The same way X already does it" is honest once X is confirmed real. Used pre-emptively it
is a fabricated mechanism wearing the clothes of a resolved one, worse than admitting the
gap because it reads as settled.

- **Before (unconfirmed):** "...a dispatcher can tell whether a week's totals are still
  moving or final via the same Provisional badge other carriers' invoices already use."
  Nobody confirmed a Provisional badge is a real, named thing.
- **After:** Either confirm the mechanism exists and name it, or drop that clause and ask.

## 5. Inventing a literal value instead of asking what it is

- **Before:** "...an unassigned dock door is clearly labelled as unassigned." (an invented
  text label)
- **Real answer, once asked:** the existing convention was a lone grey hyphen in the cell,
  not a text label at all.
- **Lesson:** ask "what does this look like today" rather than "is X the right label". The
  second can be answered yes or no while still baking in a wrong assumption about the medium
  (text, icon, hyphen or colour).

## 6. Weasel phrases beside a concrete list

- **Before:** "...at the levels that make sense (lane, carrier, depot, total cost)."
- **After:** "...at four levels: lane, carrier, depot, total cost." Drop "that make sense".
  The list already does the specific work; the phrase only invites debate about whether
  something else "makes sense" too.

## 7. A vague bullet sometimes needs deleting, not sharpening

Not every abstract bullet is a gap to fix. Check whether the scenario it describes can
occur before spending effort naming a mechanism for it.

- **Example:** an AC required telematics-sync columns to be "clearly distinguished from
  freight-cost columns". The real answer was that the two column types never share a view.
  The bullet described a collision that cannot happen; the fix was to delete it, not to
  invent a visual-distinction mechanism.

## 8. Bare ticket-key references instead of real links

"See FLT-208 AC2" as plain text in an AC description is not a link; someone still has to
create the real issue link by hand. If the tracker connection can create links, do it every
time an AC references another ticket (`tracker: link issues`).
