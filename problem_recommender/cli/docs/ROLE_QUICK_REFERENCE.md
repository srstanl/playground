# Role-Aware Generation Quick Reference

## TL;DR

The system auto-detects your career level from your description and generates problems at the right difficulty.

```bash
python3 cli/main.py
> generate
> staff swe palindrome problem in java
# ✅ Auto-detects STAFF level → generates HARD problem
```

## Role Keywords

| Role | Detection Keywords |
|------|-------------------|
| **Junior** | junior, entry, entry-level, jr, graduate |
| **Mid** | mid, mid-level, intermediate, senior-engineer |
| **Senior/Staff** | senior, sr, staff, staff-level, staff swe, staff-swe |
| **Principal** | principal, principal engineer, distinguished |

## Difficulty Mapping

| Role | Default Difficulty | Use Case |
|------|-------------------|----------|
| Junior | **Easy** | Fundamentals, basics |
| Mid | **Medium** | Balanced complexity |
| Senior/Staff | **Hard** | Advanced topics |
| Principal | **Hard** | Advanced architecture |

## Example Queries

### Junior
```
"junior array problem in python"
"entry level sorting in java"
"jr linked list in c#"
"graduate coding challenge"
```

### Mid
```
"mid level tree problem in java"
"intermediate optimization in python"
"mid-level design pattern in c#"
```

### Senior/Staff
```
"senior system design in java"
"staff swe caching in python"
"staff-level scalability in c#"
```

### Principal
```
"principal system architecture"
"principal engineer design question"
```

## No Role Detection

If no role is detected, system defaults to **Mid-Level**:
```
"sorting algorithm problem" → Mid level, Medium difficulty
```

## Override Options

```bash
What problem? > staff swe palindrome in java
Detected: STAFF level problem
Keep this role? [Y/n]: n
Select role [junior/mid/senior/principal]: junior

Use default difficulty (easy) for junior? [Y/n]: n
Difficulty [easy/medium/hard]: medium
```

## Generated Problem Components

Each problem includes:
- ✅ Title
- ✅ Role badge (👤 SENIOR)
- ✅ Difficulty level
- ✅ Language
- ✅ Role context explanation
- ✅ Problem description
- ✅ Test cases
- ✅ Hints
- ✅ Complexity info

## What Role Does

| Role | Problem Scope | Expectations |
|------|---------------|-------------|
| **Junior** | Single concept | Basic understanding |
| **Mid** | Multiple concepts | Design choices |
| **Senior** | System level | Optimization + edge cases |
| **Principal** | Architecture | Novel approaches |

## Quick Start

1. **Run the system**:
   ```bash
   python3 cli/main.py
   ```

2. **Generate a problem**:
   ```bash
   > generate
   ```

3. **Specify role in description**:
   ```
   staff swe [topic] in [language]
   ```

4. **System auto-calibrates** difficulty and generates appropriate problem

5. **Test your solution**:
   ```bash
   > test
   ```

## Pro Tips

✅ **Start at your level** - Don't jump to Principal level  
✅ **Be explicit** - "staff swe problem" is better than just "hard problem"  
✅ **Use multiple roles** - Practice at different levels for growth  
✅ **Mix languages** - Staff swe problems in Java, Python, C#  
✅ **Track progress** - See improvements across role levels  

## Common Queries

| Goal | Query |
|------|-------|
| Practice interviews | "staff swe [topic] in [language]" |
| Learn new topic | "junior [topic] in [language]" |
| Interview prep | "senior [topic] in [language]" |
| Progress check | "mid level [topic] in [language]" |

---

**Need help?** Check [cli/docs/ROLE_AWARE_GENERATION.md](cli/docs/ROLE_AWARE_GENERATION.md) for complete documentation.
