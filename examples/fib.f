PROGRAM FIB
  INTEGER N, I, A, B, T
  N = 6
  A = 0
  B = 1
  PRINT *, A
  PRINT *, B
  DO 10 I = 3, N
    T = A + B
    PRINT *, T
    A = B
    B = T
10 CONTINUE
END
