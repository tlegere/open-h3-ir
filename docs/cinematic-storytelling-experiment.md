# Cinematic storytelling experiment (base modes)

This is an **A/B experiment**, not a new validation rule or a claim that more prose makes
better video. It targets the measured user failure: a brief with valid multi-shot timings
that reads like camera labels pasted onto subjects who scarcely do anything.

## Scope

- **Control**: `h3ir/prompts/compose_base.v1.txt`
- **Experiment**: `h3ir/prompts/compose_base.v2.txt`
- **Changed default**: only base modes (T2VA / I2VA / FL2VA / L2VA) on the write-first path.
- **Unchanged**: full-reference composer, MiniMax's embedded guide, shot-count policy,
  1.2-second timing contract, validator, fallback, ComfyUI node pack, and video rendering.
- The experiment replaces a short set of craft reminders with guidance on the opening
  image, physical cause/effect, directing emotion through observable behavior, the
  reason for a cut, motivated camera changes, sound, and a silent check for visual payoff.

This explicitly does **not** demand a minimum number of shots, a camera move in every
shot, emotions invented beyond the request, an adjective quota, or a word count.
A static shot can be excellent; the shot still needs meaningful visual information.

## Evaluation protocol

1. Run `h3ir controls` and `pytest -q` before a model-based trial.
2. Use the **same** Gemma endpoint/model, shot count, duration, aspect, creativity dial,
   Director notes, original requests, and seeds from the accepted timing experiment.
   Keep H3 rendering disabled while judging the text.
3. Re-run at least 10 varied requests. Include one quiet scene, one high-energy action,
   one emotional reaction, one environment reveal, and one continuous action. Compare
   against saved control prompts generated with the *same seeds*. If a seed changed,
   label the pair as unpaired.
4. Record for each arm: first-pass vs repaired, warnings, fallback, wall time, shots,
   number of visible actions, and notes on shot-to-shot progression.
5. Blind-read each prompt without knowing its arm. Rate these dimensions from 0 to 3:
   - **Readable composition**: can someone draw the opening frame from the words?
   - **Visual development**: is action physically causal over the available seconds?
   - **Emotional engagement**: does on-screen evidence support the requested feeling?
   - **Camera purpose**: does reframing reveal something rather than call attention to itself?
   - **Payoff and continuity**: does each cut advance the moment without location/subject drift?
   Count tangible failures; no automated validator should enforce taste.
6. Only render 2-3 paired winners/losers in H3 to test *render fidelity*. Even an
   excellent prompt does not guarantee H3 will execute timed cuts as written.

**Keep the earlier timing experiment branch and its saved reports untouched.**
Do not merge this branch on syntax checks alone. The actual acceptance gate is improved
creative quality with no material regression in mechanical acceptance.

## Manual rollback

To restore the timing-only experiment, reinstall its pinned commit
`eab8ca5502d52ec23ca1219e44cde553f5e2764e` in the ComfyUI container and restart it.
