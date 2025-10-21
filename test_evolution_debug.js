// Test evolution debug script
console.log('🔍 Testing evolution debug...');

// Check if engine exists
if (window.zxEvolutionEngine) {
  console.log('✅ Engine exists');
  
  // Get initial state
  const initialSnapshot = window.zxEvolutionEngine.getSnapshot();
  console.log(`📊 Initial: nodes=${initialSnapshot.graph.nodes.length}, edges=${initialSnapshot.graph.edges.length}`);
  
  // Run evolution manually
  console.log('🔄 Running evolution manually...');
  window.zxEvolutionEngine.evolve(0.8, 0.016).then(coherence => {
    console.log(`✅ Evolution completed, coherence=${coherence}`);
    
    // Check final state
    const finalSnapshot = window.zxEvolutionEngine.getSnapshot();
    console.log(`📊 Final: nodes=${finalSnapshot.graph.nodes.length}, edges=${finalSnapshot.graph.edges.length}`);
    
    if (finalSnapshot.graph.nodes.length > initialSnapshot.graph.nodes.length) {
      console.log('🎉 Evolution working! Nodes increased');
    } else {
      console.log('❌ Evolution not working - no node increase');
    }
  }).catch(err => {
    console.error('❌ Evolution failed:', err);
  });
} else {
  console.log('❌ Engine not found');
}
