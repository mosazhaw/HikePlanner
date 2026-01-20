<script>
    import { dev } from "$app/environment";
    let url = location.protocol + "//" + location.host;
    if (dev) {
        url = "http://localhost:5000";
    }

    let downhill = 0;
    let uphill = 0;
    let length = 0;

    let prediction = "n.a.";
    let din33466 = "n.a.";
    let sac = "n.a.";

    async function predict() {
        let result = await fetch(
            url +
                "/api/predict?" +
                new URLSearchParams({
                    downhill: downhill,
                    uphill: uphill,
                    length: length,
                }),
            {
                method: "GET",
            },
        );
        let data = await result.json();
        console.log(data);
        prediction = data.time;
        din33466 = data.din33466;
        sac = data.sac;
    }
</script>

<svelte:head>
    <title>HikePlanner</title>
</svelte:head>

<div class="app-bg">
    <main class="container py-5">
        <div class="row g-4 align-items-start">
            <div class="col-lg-6">
                <div class="p-4 p-lg-5 bg-white shadow-sm rounded-4">
                    <h1 class="display-6 fw-bold mb-2">HikePlanner</h1>
                    <p class="text-muted mb-4">
                        Schätze die Gehzeit basierend auf Distanz und Höhenmetern.
                    </p>

                    <form class="vstack gap-3" on:submit|preventDefault={predict}>
                        <div>
                            <label class="form-label fw-semibold">Abwärts [m]</label>
                            <div class="row g-2 align-items-center">
                                <div class="col-4">
                                    <input
                                        type="number"
                                        class="form-control"
                                        bind:value={downhill}
                                        min="0"
                                        max="10000"
                                    />
                                </div>
                                <div class="col-8">
                                    <input
                                        type="range"
                                        class="form-range"
                                        bind:value={downhill}
                                        min="0"
                                        max="10000"
                                        step="10"
                                    />
                                </div>
                            </div>
                        </div>

                        <div>
                            <label class="form-label fw-semibold">Aufwärts [m]</label>
                            <div class="row g-2 align-items-center">
                                <div class="col-4">
                                    <input
                                        type="number"
                                        class="form-control"
                                        bind:value={uphill}
                                        min="0"
                                        max="10000"
                                    />
                                </div>
                                <div class="col-8">
                                    <input
                                        type="range"
                                        class="form-range"
                                        bind:value={uphill}
                                        min="0"
                                        max="10000"
                                        step="10"
                                    />
                                </div>
                            </div>
                        </div>

                        <div>
                            <label class="form-label fw-semibold">Distanz [m]</label>
                            <div class="row g-2 align-items-center">
                                <div class="col-4">
                                    <input
                                        type="number"
                                        class="form-control"
                                        bind:value={length}
                                        min="0"
                                        max="30000"
                                    />
                                </div>
                                <div class="col-8">
                                    <input
                                        type="range"
                                        class="form-range"
                                        bind:value={length}
                                        min="0"
                                        max="30000"
                                        step="10"
                                    />
                                </div>
                            </div>
                        </div>

                        <div class="d-grid">
                            <button class="btn btn-primary btn-lg" type="submit">
                                Predict
                            </button>
                        </div>
                    </form>
                </div>
            </div>

            <div class="col-lg-6">
                <div class="p-4 p-lg-5 bg-white shadow-sm rounded-4">
                    <div class="d-flex align-items-center justify-content-between mb-3">
                        <h2 class="h5 mb-0 fw-semibold">Ergebnisse</h2>
                        <span class="badge text-bg-light">API</span>
                    </div>
                    <div class="table-responsive">
                        <table class="table table-sm align-middle">
                            <tbody>
                                <tr>
                                    <th scope="row" class="text-muted">Dauer (Modell)</th>
                                    <td class="fw-semibold">{prediction}</td>
                                </tr>
                                <tr>
                                    <th scope="row" class="text-muted">Dauer (DIN33466)</th>
                                    <td class="fw-semibold">{din33466}</td>
                                </tr>
                                <tr>
                                    <th scope="row" class="text-muted">Dauer (SAC)</th>
                                    <td class="fw-semibold">{sac}</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                    <p class="small text-muted mb-0">
                        Werte basieren auf deinen Eingaben und der aktuellen Modellversion.
                    </p>
                </div>
            </div>
        </div>
    </main>
</div>
