# Introduction to Whitfield

Whitfield is a compiler for a domain specific language implementing
finite-field math. It was written to reduce the amount of hand-coded assembly
in cryptography libraries. For example, in [OpenSSL][openssl] there is only one
optimized elliptic curve: P-256. This one curve requires 13kloc of hand-written
assembly in addition to many other lines of C code and it only covers a handful
of processors. The resulting code is extremely fragile and difficult to debug.
Further, it is nearly impossible to audit.

Therefore, Whitfield has the following goals, in priority order:

1. **Correctness**: Whitfield must generate code that is mathematically
   correct. If we don't, nobody can use us.

2. **Test Coverage**: Whitfield does not merge functionality without complete
   test coverage. This includes benchmark support.

3. **Constant Time**: Whitfield aims to be constant time for crucial operations
   on recent processors. We do not intend to target older CPUs, but will merge
   patches for them so long as it does not conflict with our other goals.

4. **Auditability**: Whitfield compiles from a domain specific language to
   [LLVM Intermediate Representation][llvmir]. The Whitfield language, the
   compiler code and the generated output should be concise, easy to read and
   well documented. You should know what your cryptography code is doing.

5. **Performance**: Whitfield plans to output implementations of the algorithms
   which are fast. This is our least well-defined goal. However, we aim to beat
   hand-coded C.

# Example Code

First, we'll create a file `dh.wht` which will contain a function for doing
Diffie-Hellman exponentiation. This simple function simply raises `base` to
the power of `exp`, modulo some prime (TBD) and returns the result `res`:

```
do_dh(base, exp)(res) {
    res = base @ exp;
}
```

Next, we'll create a group definition in the file `mygrp.wht`. First, we'll
use the prime `2 ^ 255 - 19`. Second, we'll import our previously defined
function. Finally, we'll define a generator constant.

```
field 2 @ 255 - 19;
import dh;
gen = 2;
```

From these source files we can generate LLVM IR and a C header:

```
$ whitfield mygrp.wht mygrp.ll
$ whitfield mygrp.wht mygrp.h
```

The C header will look something like this:

```c
typedef unsigned char wht_mygrp_t[32];

extern const wht_mygrp_t wht_mygrp_gen;

void
wht_mygrp_do_dh(const wht_mygrp_t base,
                const wht_mygrp_t exp,
                      wht_mygrp_t res);
```

From here your crypto library can import the header and link against the
binary produced from LLVM.

Note that we have separated algorithm implementation from group parameters.
This algorithm (`dh.wht`) can be reused with other groups without modification.

# Current Status

Whitfield is in active development and is not ready for use.

## The Good

* Whitfield can compile its language.
* Whitfield outputs are extensively tested and benchmarked.

## The Bad

* Whitfield's language isn't stable.
* Whitfield doesn't handle input values not in the field.
* Whitfield generated code is currently slow.
* Whitfield doesn't guarantee constant time.
* Whitfield is missing a number of important algorithms, including:
  1. Full modular reduction
  2. Division (inversion)
  3. Square Root (used for point recovery in Edwards and Weierstrass curves)
* Whitfield doesn't implement advanced techniques such as precomupted tables.

# Supported Operations

* Addition: `+`
* Subtraction: `-`
* Multiplication: `*`
* Exponentiation: `@`

[openssl]: https://github.com/openssl/openssl/tree/master/crypto/ec/asm
[llvmir]: https://llvm.org/docs/LangRef.html
