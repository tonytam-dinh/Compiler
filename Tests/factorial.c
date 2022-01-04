// Dalio, Brian A.
// dalioba
// 2019-10-06

#include <stdio.h>

int main() {
  // Compute factorial of this number.
  int n = 10;

  // Resulting value.
  int fact = 1;

  // Loop up to n, doing a multiply at each step.
  for ( int i=1; i<=n; i++ ) {
    fact = fact * i;
  }

  // At this point, fact is n!.
  printf( "%d! = %d\n", n, fact );
}
