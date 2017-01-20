package main

import (
	"os"
	"bufio"
	"fmt"
	"path/filepath"
	"strings"
	"strconv"
	"encoding/binary"
	"math"
	"bytes"
	"runtime/pprof"
	"flag"
)

type bhvior struct {
 X int16
 Y int16
 Evolvability int16
 Behaviorhash int16
 solution uint8 //when reading in solution or not
}

//todo: align this with c++ maze code at some piont
func hash_behavior(x,y int) int {
 return x/10*300+y/10
}

//global
var niches=make(map[int]int,16*3)

func evolvability(indx uint32,themap map[uint32]bhvior) int {
 for k,_:=range niches {
  delete(niches,k)
 }
 for _,k := range get_neighbors(indx) {
  niches[int(themap[k].Behaviorhash)]=1
 }
 return len(niches)
}

func get_neighbors(indx uint32) []uint32 {
 ret:=make([]uint32,16*3)
 v:=decode_index(indx)
 c:=0
 for i:=0;i<16;i++  {
  oldval:=v[i]
  for j:=0;j<3;j++ {
    v[i]=j;
    ret[c]=encode_index(v)
    c++;
  }
  v[i]=oldval;
 }
 return ret
}

func decode_index(indx uint32) []int {
 ret:=make([]int,16)
 for i:=15;i>=0;i-- {
  v:=(indx%3)
  ret[i]=int(v)
  indx /= 3;
 }
 return ret
}

func encode_index(vals []int) uint32 {
 accum:=uint32(0)
 for i:=0;i<16;i++ {
  accum*=3;
  accum+=uint32(vals[i]);
 }
 return accum
}

func process_file(fname string, themap map[uint32]bhvior) {

 myFile,_ := os.Open(fname)
 defer myFile.Close()

 bfile := bufio.NewReader(myFile)

 line, _ , _ := bfile.ReadLine()
 sline := string(line);
 index1, _ := strconv.ParseUint(sline,0,32)
 index:=uint32(index1)

 txt,end,err:= bfile.ReadLine()
 var count uint32=0

 for ; err==nil && !end; txt,end,err = bfile.ReadLine() {
  stxt:=strings.Fields(string(txt))
  xf,_:=strconv.ParseFloat(stxt[0],64)
  yf,_:=strconv.ParseFloat(stxt[1],64)
  solutionf,_:=strconv.ParseFloat(stxt[2],64)
  x:=int(xf)
  y:=int(yf)
  solution:=uint8(solutionf)
  themap[index+count]=bhvior{int16(x),int16(y),int16(0),int16(hash_behavior(x,y)),solution}
  count++;
 }

}

func main() {
 var memprofile = flag.String("memprofile","","write memory profile to this file")
 flag.Parse()

 behaviorMap := make(map[uint32]bhvior)
 matches,_ := filepath.Glob("*.txt")
 for _,file := range matches {
 fmt.Println(file)
 process_file(file,behaviorMap)
 }


 genome_count:=uint32(math.Pow(3,16))
 //genome_count=uint32(300000)
 fmt.Println(genome_count)

 outfile,_ := os.Create("storage.dat")
 defer outfile.Close()
 //fmt.Println(binary.LittleEndian) 
 buf:=new(bytes.Buffer)
 for x:=uint32(0); x<genome_count;x++ {
  if x%200000==0 {
   fmt.Println(x)
  }
  data:=behaviorMap[x];
  data.Evolvability=int16(evolvability(x,behaviorMap))
  err := binary.Write(buf,binary.LittleEndian,&data)
  if err!=nil {
   fmt.Println(err)
  }
  outfile.Write(buf.Bytes())
  buf.Reset()
 }


 if *memprofile != "" { 
  f,_:=os.Create(*memprofile)
  pprof.WriteHeapProfile(f)
  f.Close()
  return
 }



}
