SOURCE_IMAGES=$(wildcard source/*.png)

all: $(patsubst source/%,backdrops/%,$(SOURCE_IMAGES)) \
     $(patsubst source/%,floors/%,$(SOURCE_IMAGES))

backdrops/%: source/% make_backdrop.py backdrops
	python make_backdrop.py -w $< $@

floors/%: source/% make_backdrop.py floors
	python make_backdrop.py -f $< $@

backdrops:
	mkdir -p backdrops

floors:
	mkdir -p floors

