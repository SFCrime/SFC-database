# General
- [ ] Need to make sure CORS is set up in a safe manner
- [ ] Switch to a limited set of values instead of booleans for each one, for the shape types
- [ ] Abstract out database url (for production vs. local)

# Visualizations
- [ ] Event-to-event comparison ("event" = date-time + geometry); Allow user to select up to 5 different dates or date ranges of equal length
- [ ] Display normalized (e.g. crime/hr) totals for each "event" and small multiples of each crime category
- [ ] Allow user to highlight points within polygon by "event"
- [ ] Color code crime categories within polygon
- [ ] Give detailed information to user after selecting individual point within polygon

# Optional visualizations
- [ ] After selecting date-time span, compare those date-times vs all others in the same calendar year (one-vs-all); consider disaggregate version as well
- [ ] After selecting date-time span, compare total # of crimes before and after (use 100% of time span on both sides)
