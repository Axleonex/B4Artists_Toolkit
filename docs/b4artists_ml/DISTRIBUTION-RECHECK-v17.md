# Publisher recheck recovered on2026-09-08

The web retriever repeatedly timed out because its requests used HTTPS. A direct public HTTP request to the [CMU motion-capture publisher](http://mocap.cs.cmu.edu/) returned200, as did its [FAQ](http://mocap.cs.cmu.edu/faqs.php). Source snapshots and SHA256 receipts are in training/b4artists_ml/results/cmu-publisher-recheck-v17.json. This resolves the previously recorded fresh-publisher retrieval gap; earlier timeout receipts remain valid history.

The publisher permits research use and inclusion in commercially sold products, but prohibits selling the data itself, including converted data. It requests acknowledgement of the dataset source and NSF funding. Existing model cards retain attribution; raw motion is not in the installable ZIP. This source finding is evidence about CMU data use, not blanket clearance for unrelated code, models, future datasets or the optional Cascadeur connector.

The publisher also confirms that a person can have multiple subject IDs. Therefore our catalog-prefix folds do not establish actor-independent validation. It warns about lower-quality early sessions and noisy hand/toe joints; fingers/thumbs are not captured. These limitations matter for future corpus expansion and motion-quality evaluation. The current frozen v17 experiment, original thresholds and all old holdouts remain unchanged.

No motion archive, new training clip, third-party model or service was acquired. HTTP evidence is retained with its transport explicitly recorded; no authentication or private material was involved.
