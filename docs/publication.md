# Publishing CROSSWIRE

The GitHub repository is [kai9987kai/CROSSWIRE](https://github.com/kai9987kai/CROSSWIRE). The Hugging Face repository is the public static Space [Kai9987kai/CROSSWIRE](https://huggingface.co/spaces/Kai9987kai/CROSSWIRE). Its portal links to the source, evidence and downloadable packages. Run the interactive Python workbench locally using the README commands. Creating a compute-backed Space was rejected with HTTP 402 because the publishing account requires a PRO subscription; no paid service was enabled.

## Source identity and artifacts

The publication tag is `crosswire-formal-synthesis-2026-11-03`. GitHub and Hugging Face have different commit IDs because their repository histories differ. The Hugging Face `release-manifest.json` records the owning GitHub commit, Python source identity, study scientific hashes, artifact hashes and a SHA-256/size inventory of the published payload. Its inventory excludes the manifest itself to avoid a self-reference. The inventory hash binds that complete list; hashes identify content and do not establish scientific correctness.

The Hub source files are exported from committed Git blobs, preserving canonical line endings and historical receipt contents. Local Windows checkout line endings can differ. Build the wheel and source package from that exported snapshot, then run the isolated package checker against the same snapshot. This keeps Python modules and web assets byte-identical between the source payload and installed package.

Packages live under `artifacts/` on Hugging Face. The wheel contains the runtime and web assets; the source archive also contains tests, protocols, research, receipts, documentation and the static portal. Caches, local environments, process logs and scratch checkpoints are excluded. The MIT license remains unchanged. Existing remote history and policy files are preserved; publishing uses ordinary pushes and additive Hub commits.

## Checks before reporting publication complete

1. Inspect intended paths, confirm the verified Python source identity and preserve historical receipt Git blobs.
2. Check the staged diff, commit, and export the committed source. Build both packages and verify their inventories and an isolated installation outside the source tree.
3. Push the GitHub commit/tag and upload the matching Hub payload without deleting unrelated remote files. Pin the Hub tag to the upload commit.
4. Resolve both tags, compare local and remote GitHub heads, and verify every Hub payload file against its SHA-256 and size. Verify preserved remote policy files separately.
5. Check GitHub Actions for the exact published commit and inspect the hosted static portal on desktop/mobile. Report compute hosting separately from source publication.

The bounded-planning results and limitations remain in [the verification report](verification-budgeted-experiments.md) and [the dated research synthesis](../research/2026-11-01-budgeted-experiments.md). Public model checking, exact replay, hosted UI checks and CI validate different aspects of the software; none establishes real-world safety or a general performance advantage.

Hugging Face configuration follows the official [Static Spaces guide](https://huggingface.co/docs/hub/en/spaces-sdks-static) and [configuration reference](https://huggingface.co/docs/hub/en/spaces-config-reference).
