

(define m (sal/module "(@ system (bakery () (5 15)))"))
(define m1 (sal-module/flat m))
(define m2 (sal-ast/expand m1))
(define m3 (sal-ast/expand-quantifiers m2))
(define m4 (sal-ast/cse m3))
(define m5 (sal-ast->boolean-ast m4))