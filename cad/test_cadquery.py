"""Quick test to verify CadQuery is working properly."""

import cadquery as cq
import time

def test_simple_box():
    """Test creating a simple box - should be very fast."""
    start = time.time()
    result = cq.Workplane("XY").box(10, 10, 10)
    elapsed = time.time() - start
    print(f"Simple box: {elapsed:.3f}s")
    return elapsed

def test_multiple_cuts():
    """Test what happens when we cut many holes individually."""
    start = time.time()
    box = cq.Workplane("XY").box(30, 30, 10)

    # Cut 10 holes individually (similar to your speaker grille pattern)
    for i in range(10):
        hole = cq.Workplane("XY").center(i*2, 0).circle(0.5).extrude(11)
        box = box.cut(hole)

    elapsed = time.time() - start
    print(f"10 individual cuts: {elapsed:.3f}s")
    return elapsed

def test_combined_cuts():
    """Test cutting holes all at once - much faster."""
    start = time.time()
    box = cq.Workplane("XY").box(30, 30, 10)

    # Create all holes on same workplane before cutting
    holes = cq.Workplane("XY")
    for i in range(10):
        holes = holes.center(i*2, 0).circle(0.5)

    holes = holes.extrude(11)
    box = box.cut(holes)

    elapsed = time.time() - start
    print(f"Combined cuts: {elapsed:.3f}s")
    return elapsed

if __name__ == "__main__":
    print("Testing CadQuery performance...\n")

    test_simple_box()
    test_multiple_cuts()
    test_combined_cuts()

    print("\nCadQuery is working!")
