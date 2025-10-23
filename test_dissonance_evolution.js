const { ResonanceDrivenEngine } = await import('./FractalRecursiveCoherence/FIRM-Core/FIRM_ui/resonance_driven_engine.js');
const { ObjectG } = await import('./FractalRecursiveCoherence/FIRM-Core/FIRM_ui/FIRM_dsl/core.js');
const assert = await import('assert');

async function runTest() {
    console.log('Testing dissonance-driven evolution...');

    const engine = new ResonanceDrivenEngine();
    await engine.initializeGraph(); // Ensure engine is ready
    
    // Create a simple, somewhat dissonant graph (a line of nodes with varied phases)
    const dissonantGraph = new ObjectG({
        nodes: [0, 1, 2, 3],
        edges: [[0, 1], [1, 2], [2, 3]],
        labels: {
            0: { kind: 'Z', phase_numer: 1, phase_denom: 8, monadic_id: 'node_0' },
            1: { kind: 'X', phase_numer: 5, phase_denom: 8, monadic_id: 'node_1' },
            2: { kind: 'Z', phase_numer: 3, phase_denom: 8, monadic_id: 'node_2' },
            3: { kind: 'X', phase_numer: 7, phase_denom: 8, monadic_id: 'node_3' }
        }
    });

    engine.currentGraph = dissonantGraph;

    const initialDissonance = engine.calculateAuditoryDissonance(engine.currentGraph);
    console.log(`Initial dissonance: ${initialDissonance}`);

    // Run the evolution step
    await engine.applyResonanceEvolution(1.0);

    const finalDissonance = engine.calculateAuditoryDissonance(engine.currentGraph);
    console.log(`Final dissonance: ${finalDissonance}`);

    assert.strict(finalDissonance < initialDissonance, 
        `Test Failed: Evolution should decrease dissonance. Initial: ${initialDissonance}, Final: ${finalDissonance}`);

    console.log('✅ Test Passed: Evolution successfully decreased auditory dissonance.');
}

runTest().catch(err => {
    console.error('❌ Test Failed:', err.message);
    process.exit(1);
});
