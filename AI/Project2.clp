(deftemplate sparse
  (slot index
    (type INTEGER)
    (default 0))
  (slot value
    (type INTEGER)
    (default 0))
  )

(deffacts initial "non-zero elements"
  (sparse (index 1) (value 42))
  (sparse (index 4) (value 17))
  (sparse (index 7) (value 23))
  (sparse (index 8) (value 14)))

(defrule DeleteRule
  (del-item ?i)
  ?fact1 <- (del-item ?i)
  ?fact2 <- (sparse
              (index ?i) (value ?))
  =>
  (retract ?fact1 ?fact2)
  (printout t "Deleted element" crlf crlf)
)

(defrule CheckDuplicate
  (add-item ?i ?v)
  ?fact1 <- (add-item ?i ?v)
  (retract ?fact1)
  (not (sparse (index ?i) (value ?)))
  =>
  (assert (sparse (index ?i) (value ?v)))
  (printout t "Duplicate index" crlf)
  (retract ?fact1))

(defrule Clean
  ?fact <- (add-item ? ?)
  =>
  (retract ?fact))

;(defrule QueryRule
  ;(del-item ?i)
  ;=>
  ;(printout t "Enter the index of the item that you want to delete:" crlf crlf)
  ;;(assert (dindex (explode$ (readline))))
;)

;(defrule DeleteRule
  ;(del-item ?)
  ;?fact1 <- (dindex ?dindex)
  ;?fact2 <- (sparse
              ;(index ?dindex) (value ?))
  ;=>
  ;(retract ?fact1 ?fact2)
;)

