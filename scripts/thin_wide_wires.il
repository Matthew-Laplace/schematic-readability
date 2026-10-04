/* Global thin-wire pass for one schematic cellview.
   Every remaining wide "path" (width 0.0125) becomes a width-0 wire on the
   same centre-line, and every wire label that owned a net name is re-created
   glued to the new wire.  Root cause of the earlier failures: schCreateWire
   returns a LIST of wire ids, so the old scripts passed a list as the glue
   argument and schCreateWireLabel silently failed (SCH-1001).
   Gates: G1 electrical map + label inventory identical, G2 schCheck 0/0.  */
TW_LIB = nil
TW_CELL = nil
TW_CV = nil
TW_ERR = nil
TW_LABS_SAVED = nil

/* Parameterized copy of the converter verified on LIB/CELL/schematic
   (2026-09-18, 36 wide bars -> thin lines, both gates passed).  Caller must
   set TW_LIB / TW_CELL, then run TW_OPEN, TW_PRE=TW_SNAP(), TW_RUN(), the two
   gates, and only then TW_SAVE or TW_ABORT.  Not yet re-run on a second cell.*/

procedure( TW_S( x )
  if( x == nil "NONE" sprintf(nil "%L" x) )
)
procedure( TW_OPEN( dwrLib dwrCell )
  prog(( cv )
    TW_LIB = dwrLib
    TW_CELL = dwrCell
    cv = dbOpenCellViewByType( TW_LIB TW_CELL "schematic" "" "a")
    if( cv == nil return( list("ERROR open") ) )
    TW_CV = cv
    return( list("OPEN ok") )
  )
)
procedure( TW_ABORT()
  prog(( i )
    when( TW_CV != nil
      for( i 1 16 errset( dbClose( TW_CV ) ) )
      TW_CV = nil )
    return( list("ABORTED without save") )
  )
)
procedure( TW_SAVE()
  prog(( i )
    if( dbSave( TW_CV ) == nil return( list("ERROR dbSave") ) )
    for( i 1 16 errset( dbClose( TW_CV ) ) )
    TW_CV = nil
    return( list("SAVED LIB/CELL/schematic") )
  )
)
procedure( TW_SNAP()
  prog(( cv out sh )
    cv = TW_CV
    out = nil
    foreach( inst cv~>instances
      foreach( it inst~>instTerms
        out = cons( sprintf(nil "IT %s/%s=%s" TW_S(inst~>name) TW_S(it~>name)
                     TW_S(car(errset(it~>net~>name))) ) out ) ) )
    foreach( tm cv~>terminals
      out = cons( sprintf(nil "TT %s=%s dir=%s" TW_S(tm~>name)
                   TW_S(car(errset(tm~>net~>name))) TW_S(tm~>direction) ) out ) )
    foreach( sh cv~>shapes
      when( sh~>objType == "label"
        out = cons( sprintf(nil "LB %s|%L|%L|%L|%L" TW_S(car(errset(sh~>theLabel)))
                     car(errset(sh~>height)) car(errset(sh~>orient))
                     car(errset(sh~>justify)) car(errset(sh~>xy)) ) out ) ) )
    foreach( net cv~>nets
      out = cons( sprintf(nil "NET %s" TW_S(car(errset(net~>name))) ) out ) )
    out = cons( sprintf(nil "COUNTS insts=%d nets=%d shapes=%d terminals=%d labels=%d paths=%d"
                 length(cv~>instances) length(cv~>nets) length(cv~>shapes)
                 length(cv~>terminals)
                 length( setof( x cv~>shapes x~>objType == "label" ) )
                 length( setof( x cv~>shapes x~>objType == "path" ) ) ) out )
    return( sort( out 'alphalessp ) )
  )
)
procedure( TW_IN( bb outer )
  prog(( cx cy )
    cx = (car(car(bb)) + car(cadr(bb))) / 2.0
    cy = (cadr(car(bb)) + cadr(cadr(bb))) / 2.0
    return( cx >= car(car(outer)) && cx <= car(cadr(outer))
         && cy >= cadr(car(outer)) && cy <= cadr(cadr(outer)) )
  )
)
procedure( TW_LABELS_ALL()
  prog(( out sh )
    out = nil
    foreach( sh TW_CV~>shapes
      when( sh~>objType == "label"
        out = cons( list( car(errset(sh~>theLabel)) car(errset(sh~>height))
                          car(errset(sh~>orient)) car(errset(sh~>justify))
                          car(errset(sh~>font)) car(errset(sh~>xy)) ) out ) ) )
    return( out )
  )
)
procedure( TW_HAS_LABEL( lab )
  prog(( hit )
    hit = nil
    foreach( sh TW_CV~>shapes
      when( sh~>objType == "label" && car(errset(sh~>theLabel)) == car(lab)
            && car(errset(sh~>xy)) == cadr(cddddr(lab))
        hit = t ) )
    return( hit )
  )
)
procedure( TW_PUT( wire lab )
  prog(( res )
    res = errset( schCreateWireLabel( TW_CV wire cadr(cddddr(lab))
                  car(lab) cadddr(lab) caddr(lab) car(cddddr(lab))
                  if( cadr(lab) == nil 0.0625 cadr(lab) ) nil ) )
    when( res == nil TW_ERR = errset.errset )
    return( res != nil )
  )
)
procedure( TW_FIND_WIRE( xy tol )
  prog(( hit bb )
    hit = nil
    foreach( sh TW_CV~>shapes
      when( hit == nil && sh~>objType == "line"
        bb = car(errset( sh~>bBox ))
        when( bb != nil
          when( car(xy) >= car(car(bb)) - tol && car(xy) <= car(cadr(bb)) + tol
                && cadr(xy) >= cadr(car(bb)) - tol
                && cadr(xy) <= cadr(cadr(bb)) + tol
            hit = sh ) ) ) )
    return( hit )
  )
)
/* exact containment first, then a one-grid tolerance as the fallback */
procedure( TW_FIND_WIRE2( xy )
  prog(( w )
    w = TW_FIND_WIRE( xy 0.0 )
    when( w == nil w = TW_FIND_WIRE( xy 0.0625 ) )
    return( w )
  )
)
procedure( TW_RUN()
  prog(( cv bars sh bar labs pts wire n nlab nmiss fixed labsall wire2 sh2 )
    cv = TW_CV
    n = 0  nlab = 0  nmiss = 0  fixed = 0
    labsall = TW_LABELS_ALL()
    TW_LABS_SAVED = labsall
    bars = nil
    foreach( sh cv~>shapes when( sh~>objType == "path" bars = cons(sh bars) ) )
    foreach( bar bars
      labs = nil
      foreach( sh2 cv~>shapes
        when( sh2~>objType == "label" && TW_IN( sh2~>bBox bar~>bBox )
          labs = cons( list( car(errset(sh2~>theLabel)) car(errset(sh2~>height))
                            car(errset(sh2~>orient)) car(errset(sh2~>justify))
                            car(errset(sh2~>font)) car(errset(sh2~>xy)) ) labs ) ) )
      pts = car(errset(bar~>points))
      dbDeleteObject(bar)
      wire = car(car(errset( schCreateWire( cv "draw" "" pts 0.0625 0.0625 0 ) )))
      if( wire == nil
        n = n - 1
        progn(
          n = n + 1
          foreach( lab labs
            when( TW_PUT( wire lab ) nlab = nlab + 1 ) ) ) ) )
    /* second pass : any label of the original inventory that is still missing
       is glued to the nearest wire that runs through its old location      */
    foreach( lab labsall
      unless( TW_HAS_LABEL( lab )
        progn(
          nmiss = nmiss + 1
          wire2 = TW_FIND_WIRE2( cadr(cddddr(lab)) )
          when( wire2 != nil
            when( TW_PUT( wire2 lab ) fixed = fixed + 1 ) ) ) ) )
    return( list( sprintf(nil "RUN bars=%d converted=%d labels-glued=%d repairs=%d repaired=%d still-missing=%d paths-left=%d labels=%d nets=%d"
                   length(bars) n nlab nmiss fixed difference(nmiss fixed)
                   length( setof( x cv~>shapes x~>objType == "path" ) )
                   length( setof( x cv~>shapes x~>objType == "label" ) )
                   length(cv~>nets) ) ) )
  )
)
/* repair-only driver : re-glue every label of the current inventory that is
   missing, using a wire that runs through the label position                */
procedure( TW_REPAIR()
  prog(( labsall lab nmiss fixed wire2 )
    labsall = TW_LABS_SAVED
    when( labsall == nil labsall = TW_LABELS_ALL() )
    nmiss = 0  fixed = 0
    foreach( lab labsall
      unless( TW_HAS_LABEL( lab )
        progn(
          nmiss = nmiss + 1
          wire2 = TW_FIND_WIRE2( cadr(cddddr(lab)) )
          when( wire2 != nil
            when( TW_PUT( wire2 lab ) fixed = fixed + 1 ) ) ) ) )
    return( list( sprintf(nil "REPAIR missing=%d fixed=%d labels=%d nets=%d check=%L"
                   nmiss fixed
                   length( setof( x TW_CV~>shapes x~>objType == "label" ) )
                   length(TW_CV~>nets) errset(schCheck(TW_CV)) )
                 sprintf(nil "lasterr=%L" TW_ERR) ) )
  )
)
