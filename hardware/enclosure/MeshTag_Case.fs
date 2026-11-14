FeatureScript 3112;
import(path : "onshape/std/common.fs", version : "3112.0");

// ============================================================================
//  MeshTag enclosure — Apple-style pebble (parametric, generated).
//  Case frame (mm): origin = board centre, z = 0 board top face, +z = front.
//  Board disc R25, z in [-1, 0]. Component envelopes baked from the KiCad STEP.
//
//  Design direction (reviewed): the FRONT is a blank warm-white ceramic dome.
//  Everything functional lives on the BACK — magnetic charge dish, slide switch,
//  user button. The LED glows through a locally thinned front wall (no hole).
//  Single continuous equator seam, symmetric edge radii.
//  Ø53.7 mm, ~11 mm tall. Min skin-to-component clearance >= 0.3 mm.
// ============================================================================
const MM = millimeter;

const RO     = 26.85 * MM;  // outer radius (Ø53.7)
const RI     = 25.25 * MM;  // cavity radius = board R25 + 0.25
const TF     = 1.40 * MM;   // front skin
const RE     = 1.60 * MM;   // edge radius (front & back, equal)
const RDOME  = 95.0 * MM;   // front dome sphere radius (more domed)
const ZA     = 8.40 * MM;   // front apex height
const ZSEAM  = -0.40 * MM;  // equator seam (front meets back)
const ZIN    = -1.90 * MM;  // inner floor of back lid
const RDBACK = 150.0 * MM;  // back dome sphere radius (gentle)
const ZBA    = -4.20 * MM;  // back apex (below board)
const GLOWT  = 0.45 * MM;   // residual wall over the LED (diffuses, no hole)

const J5_C   = vector(14.142, 14.142) * MM;  const J5_ROT = -45 * degree;   // charge pogo (on PCB front, under dome)
const SW1_C  = vector(12.985, -12.784) * MM;                                // button
const LED_C  = vector(16.160, -16.080) * MM;                                // bicolour LED
const LEVER  = vector(cos(225 * degree), sin(225 * degree)) * 21.35 * MM;   // slide-switch lever tip

const C_BODY  = color(0.949, 0.945, 0.929);  // #F2F1ED warm near-white
const C_METAL = color(0.843, 0.843, 0.855);  // #D7D7DA charge ring
const C_DARK  = color(0.80, 0.80, 0.83);     // switch/button, felt not seen
const C_GLOW  = color(0.93, 0.90, 0.84);     // LED diffuser seat (warm, subtle)

function frontZ(r)
{
    const csz = ZA - RDOME;
    const cx  = RO - RE;
    const zc  = csz + sqrt((RDOME - RE)^2 - cx^2);
    const rT  = RDOME * (cx / (RDOME - RE));
    if (r <= rT) return csz + sqrt(RDOME^2 - r^2);
    return zc + sqrt(max(RE^2 - (r - cx)^2, 0 * MM^2));
}

function backZ(r)   // outer back surface (points to -z), gentle dome
{
    const csz = ZBA + RDBACK;
    const cx  = RO - RE;
    const zc  = csz - sqrt((RDBACK - RE)^2 - cx^2);
    const rT  = RDBACK * (cx / (RDBACK - RE));
    if (r <= rT) return csz - sqrt(RDBACK^2 - r^2);
    return zc - sqrt(max(RE^2 - (r - cx)^2, 0 * MM^2));
}

function solidOf(id is Id) returns Query { return qBodyType(qCreatedBy(id + "op", EntityType.BODY), BodyType.SOLID); }

function revol(context is Context, id is Id, pts is array)
{
    var sk = newSketchOnPlane(context, id + "sk", { "sketchPlane" :
            plane(vector(0, 0, 0) * MM, vector(0, 1, 0), vector(1, 0, 0)) });
    skPolyline(sk, "p", { "points" : append(pts, pts[0]) });
    skSolve(sk);
    opRevolve(context, id + "op", { "entities" : qSketchRegion(id + "sk"),
            "axis" : line(vector(0, 0, 0) * MM, vector(0, 0, 1)), "angleForward" : 360 * degree });
}

function cylTool(context is Context, id is Id, c is Vector, rad, z0, z1)
{
    var sk = newSketchOnPlane(context, id + "sk", { "sketchPlane" : plane(vector(c[0], c[1], z0), vector(0, 0, 1)) });
    skCircle(sk, "c", { "center" : vector(0, 0) * MM, "radius" : rad });
    skSolve(sk);
    opExtrude(context, id + "op", { "entities" : qSketchRegion(id + "sk"),
            "direction" : vector(0, 0, 1), "endBound" : BoundingType.BLIND, "endDepth" : z1 - z0 });
}

function obroundTool(context is Context, id is Id, c is Vector, rot, half, rad, z0, z1)
{
    var sk = newSketchOnPlane(context, id + "sk", { "sketchPlane" :
            plane(vector(c[0], c[1], z0), vector(0, 0, 1), vector(cos(rot), sin(rot), 0)) });
    skRectangle(sk, "r", { "firstCorner" : vector(-half, -rad), "secondCorner" : vector(half, rad) });
    skCircle(sk, "c1", { "center" : vector(-half, 0 * MM), "radius" : rad });
    skCircle(sk, "c2", { "center" : vector(half, 0 * MM), "radius" : rad });
    skSolve(sk);
    opExtrude(context, id + "op", { "entities" : qSketchRegion(id + "sk"),
            "direction" : vector(0, 0, 1), "endBound" : BoundingType.BLIND, "endDepth" : z1 - z0 });
}

function boxTool(context is Context, id is Id, c is Vector, rot, hx, hy, z0, z1)
{
    var sk = newSketchOnPlane(context, id + "sk", { "sketchPlane" :
            plane(vector(c[0], c[1], z0), vector(0, 0, 1), vector(cos(rot), sin(rot), 0)) });
    skRectangle(sk, "r", { "firstCorner" : vector(-hx, -hy), "secondCorner" : vector(hx, hy) });
    skSolve(sk);
    opExtrude(context, id + "op", { "entities" : qSketchRegion(id + "sk"),
            "direction" : vector(0, 0, 1), "endBound" : BoundingType.BLIND, "endDepth" : z1 - z0 });
}

function sub(context is Context, id is Id, toolId is Id, targetId is Id)
{
    opBoolean(context, id, { "tools" : solidOf(toolId), "targets" : solidOf(targetId),
            "operationType" : BooleanOperationType.SUBTRACTION });
}

function uni(context is Context, id is Id, a is Id, b is Id)
{
    opBoolean(context, id, { "tools" : qUnion([solidOf(a), solidOf(b)]),
            "operationType" : BooleanOperationType.UNION });
}

function name(context is Context, id is Id, n is string, col is Color)
{
    setProperty(context, { "entities" : solidOf(id), "propertyType" : PropertyType.NAME, "value" : n });
    setProperty(context, { "entities" : solidOf(id), "propertyType" : PropertyType.APPEARANCE, "value" : col });
}

annotation { "Feature Type Name" : "MeshTag Case" }
export const meshtagCase = defineFeature(function(context is Context, id is Id, definition is map)
    precondition
    {
        annotation { "Name" : "Build enclosure" }
        definition.build is boolean;
    }
    {
        const NS = 48;

        // ================= FRONT SHELL (blank dome) =================
        var fo = [];
        for (var i = 0; i <= NS; i += 1) { const r = RO * i / NS; fo = append(fo, vector(r, frontZ(r))); }
        fo = append(fo, vector(RO, ZSEAM));
        fo = append(fo, vector(0 * MM, ZSEAM));
        revol(context, id + "fo", fo);

        var fi = [];
        for (var i = 0; i <= NS; i += 1) { const r = RI * i / NS; fi = append(fi, vector(r, frontZ(r) - TF)); }
        fi = append(fi, vector(RI, ZSEAM - 12 * MM));
        fi = append(fi, vector(0 * MM, ZSEAM - 12 * MM));
        revol(context, id + "fi", fi);
        sub(context, id + "f1", id + "fi", id + "fo");

        // LED glow: thin the inner wall over the LED to GLOWT, no through-hole.
        const zLedOut = frontZ(sqrt(LED_C[0]^2 + LED_C[1]^2));
        cylTool(context, id + "ledc", LED_C, 1.8 * MM, zLedOut - TF - 3 * MM, zLedOut - GLOWT);
        sub(context, id + "f2", id + "ledc", id + "fo");

        // keyring lobe fused to the front rim (opposite the components, blended)
        const lDir = vector(cos(232 * degree), sin(232 * degree));
        const lC   = lDir * (RO - 0.5 * MM);
        cylTool(context, id + "lobe", lC + lDir * 3.2 * MM, 5.0 * MM, ZSEAM, frontZ(RO) - 0.2 * MM);
        uni(context, id + "lobeU", id + "fo", id + "lobe");
        cylTool(context, id + "lh", lC + lDir * 4.4 * MM, 1.4 * MM, ZSEAM - 1 * MM, 9 * MM);
        sub(context, id + "f3", id + "lh", id + "fo");
        name(context, id + "fo", "MeshTag Front", C_BODY);

        // ================= BACK SHELL (flat floor, matched edge roll) =================
        const ZBOTF = -3.30 * MM;                 // outer back floor
        var bo = [
            vector(0 * MM, ZBOTF),
            vector(RO - RE, ZBOTF),
            vector(RO, ZBOTF + RE),
            vector(RO, ZSEAM - 0.08 * MM),
            vector(0 * MM, ZSEAM - 0.08 * MM)
        ];
        revol(context, id + "bo", bo);
        var bi = [
            vector(0 * MM, ZIN),
            vector(RI - 0.15 * MM, ZIN),
            vector(RI - 0.15 * MM, ZSEAM - 0.08 * MM),
            vector(0 * MM, ZSEAM - 0.08 * MM)
        ];
        revol(context, id + "bi", bi);
        sub(context, id + "b1", id + "bi", id + "bo");

        // charge dish recessed into the back floor (over the pogo), 0.5 mm deep
        obroundTool(context, id + "j5", J5_C, J5_ROT, 7.2 * MM, 4.3 * MM, ZBOTF - 0.25 * MM, 9 * MM);
        sub(context, id + "b2", id + "j5", id + "bo");

        // button bore through the back floor (over SW1)
        cylTool(context, id + "sw1b", SW1_C, 3.6 * MM, ZBOTF - 0.5 * MM, 9 * MM);
        sub(context, id + "b3", id + "sw1b", id + "bo");

        // slide-switch slot through the back floor (over the lever)
        boxTool(context, id + "bslot", LEVER, 45 * degree, 5.0 * MM, 1.55 * MM, ZBOTF - 0.5 * MM, ZIN + 0.5 * MM);
        sub(context, id + "b4", id + "bslot", id + "bo");

        const lDirB = vector(cos(232 * degree), sin(232 * degree));
        const lCB   = lDirB * (RO - 0.5 * MM);
        cylTool(context, id + "lobeb", lCB + lDirB * 3.2 * MM, 5.0 * MM, ZBOTF + RE - 0.2 * MM, ZSEAM - 0.08 * MM);
        uni(context, id + "lobeBU", id + "bo", id + "lobeb");
        cylTool(context, id + "lhb", lCB + lDirB * 4.4 * MM, 1.4 * MM, ZBOTF - 1 * MM, 9 * MM);
        sub(context, id + "b5", id + "lhb", id + "bo");
        name(context, id + "bo", "MeshTag Back", C_BODY);

        // ================= METAL CHARGE RING (flush thin inlay around the dish) =================
        obroundTool(context, id + "ring", J5_C, J5_ROT, 7.2 * MM, 4.6 * MM, ZBOTF - 0.25 * MM, ZBOTF + 0.02 * MM);
        obroundTool(context, id + "ringi", J5_C, J5_ROT, 7.2 * MM, 4.25 * MM, ZBOTF - 0.6 * MM, 9 * MM);
        sub(context, id + "ringc", id + "ringi", id + "ring");
        name(context, id + "ring", "Charge Ring", C_METAL);

        // ================= BUTTON CAP (flush in back floor) =================
        cylTool(context, id + "btn", SW1_C, 3.45 * MM, ZBOTF - 0.2 * MM, ZBOTF + 0.6 * MM);
        cylTool(context, id + "btns", SW1_C, 2.3 * MM, ZBOTF + 0.3 * MM, 1.95 * MM);
        uni(context, id + "btnu", id + "btn", id + "btns");
        name(context, id + "btn", "Button", C_DARK);

        // ================= LED LENS (front diffuser seat) =================
        cylTool(context, id + "lens", LED_C, 1.75 * MM, zLedOut - GLOWT - 0.5 * MM, zLedOut - GLOWT - 0.02 * MM);
        name(context, id + "lens", "LED Lens", C_GLOW);

        // ================= SLIDE ACTUATOR (flush in back floor) =================
        boxTool(context, id + "sa", LEVER, 45 * degree, 4.0 * MM, 1.25 * MM, ZBOTF - 0.2 * MM, ZBOTF + 0.6 * MM);
        boxTool(context, id + "sanib", LEVER, 45 * degree, 1.3 * MM, 0.85 * MM, ZBOTF + 0.3 * MM, 0.55 * MM);
        uni(context, id + "sau", id + "sa", id + "sanib");
        name(context, id + "sa", "Slide Switch", C_DARK);
        }, { "build" : true });

annotation { "Feature Type Name" : "Test Case" }
export const testCase = defineFeature(function(context is Context, id is Id, definition is map)
    precondition { }
    { meshtagCase(context, id + "c", { "build" : true }); }, { });
