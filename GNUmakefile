
all: $(patsubst source/%,backdrops/%,source/*.png)

backdrops/%: source/% make_backdrop.py backdrops
	python make_backdrop.py -w $< $@

backdrops:
	mkdir -p backdrops

