// Dalio, Brian A.
// dalioba
// 2019-10-31

#include <stdio.h>

int main() {
  // Compute this fibonacci number.
  int n = 10;

  // Some temporaries.
  int previous = 0;       // Fibonacci(0) = 0
  int current  = 1;       // Fibonacci(1) = 1
  int next;

  // Loop n-1 times to compute Fibonacci(n).
  // (We already know Fibonacci(1) as a base case.)
  for ( int i=2; i<=n; i++ ) {
    // next is now Fibbonaci(i)
    next     = previous + current;

    // Remember the last two Fibonacci numbers for
    // the next iteration.
    previous = current;
    current  = next;
  }

  // At this point, current is Fibonacci(n).
  printf( "fibonacci(%d) = %d\n", n, current );
}
