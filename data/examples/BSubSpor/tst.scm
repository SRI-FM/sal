

(set-verbosity! 10)
(define a1 (sal/assertion-name "(@ sporulate2 BSubSpor78ABS)"))
(define a2 (sal-assertion/flat a1))
(define a3 (sal/simplify a2))
(define a4 (sal-ast/expand a3))
(define a5 (sal-ast/cse a4))
(sal-flat-module/relevant-state-vars-dependencies (slot-value a5 :module))
(define a6 (sal-ast->boolean-ast a5))
(sal-flat-module/relevant-state-vars-dependencies (slot-value a6 :module))
