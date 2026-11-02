# ZIP-to-county handoff — review only

Care & Support and the outdoor destination page reuse the existing ZIP lookup and local county-boundary geometry. A supported ZIP lookup point suggests a Mid-Hudson county and offers a button to Community Burden & Action. In Planning, a new location suggestion sets the report selector once; subsequent manual selections remain editable. No ZIP prefix guessing or nearest-county matching.

An unresolved ZIP or a location outside the seven-county coverage offers “Explore the New York pilot” instead, with explicit coverage text. It never labels pilot data as evidence for an unsupported county. Nationwide care-resource links remain unchanged. A ZIP can cross county boundaries: users must confirm the actual county. Lookup outages remain unresolved rather than guessed.

Only a session-only location hint is carried over, not notes, symptoms, costs or survey contributions. Existing geographic lookup uses the existing external provider; no new provider/storage added. These additions are subsequent development, not claims about the original submitted MVP. No merge or deployment.

Validation: four new tests cover supported mapping, unsupported mapping, unavailable/invalid input, changed destinations and manual override. Python compilation passed. Existing geographic and professional-review tests run separately. Live ZIP-provider access and deployed behavior have not been verified in this restricted environment.
